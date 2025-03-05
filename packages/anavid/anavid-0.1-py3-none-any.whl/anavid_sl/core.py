import gc
import cv2
import copy
import torch
import time
import numpy as np
import pytorchvideo
import  torchvision
import openvino.runtime as ov
from openvino.runtime import Core

from pytorchvideo.transforms.functional import _interpolate_opencv
from pytorchvideo.models.hub import slowfast_r50_detection
from typing import Any, List, Dict, Tuple, Optional
from ultralytics import YOLO


import torch
import numpy as np
import copy
from typing import List, Optional, Tuple
from ultralytics import YOLO
from .utils import UniformTemporalSubsample_Dict_Multi_Pathway,Normalize_Dict,rescale_with_boxes 
import os



def load_openvino_model(xml_path,bin_path):
    """
    Loads an OpenVINO model from XML and BIN files.

    Args:
        xml_path (str): Path to the model XML file. Defaults to the specified path inside the 'models' folder.
        bin_path (str): Path to the weights BIN file. Defaults to the specified path inside the 'models' folder.

    Returns:
        openvino.runtime.Model: Loaded OpenVINO model.
    """
    core = Core()
    model = core.read_model(xml_path, bin_path)
    print("model loaded sucessfully !! ")
    compiled_model = core.compile_model(model, "CPU")
    return compiled_model

def person_detector(
    frame: Optional[np.ndarray] = None,
    yolo_model: str = 'yolov8n.pt',
    roi: Optional[Tuple[int, int, int, int]] = None
) -> List[np.ndarray]:
    """
    Detects persons in a given frame using a YOLO model.

    Args:
       frame (np.ndarray): The input image/frame for detection (Required).
       yolo_model (str): The YOLO model to use. Must be one of:
        - 'yolov8n.pt' (Nano)
        - 'yolov8s.pt' (Small)
        - 'yolov8m.pt' (Medium)
        - 'yolov8l.pt' (Large)
        - 'yolov8x.pt' (Extra Large)
       roi (Tuple[int, int, int, int], optional): Region of Interest (ROI) as (xmin, ymin, xmax, ymax).
        - If `None`, the entire frame is used as the ROI.

    Returns:
    List[np.ndarray]: List of detected person bounding boxes.
    """

    # Raise an error if frame is not provided
    if frame is None:
        raise ValueError("Error: 'frame' cannot be None. Please provide a valid image/frame.")

    # Get frame dimensions
    frame_height, frame_width = frame.shape[:2]

    # If ROI is not set, default to the entire frame
    if roi is None:
        roi = (0, 0, frame_width, frame_height)  # Full frame as ROI
    else:
        xmin, ymin, xmax, ymax = roi
        if not (0 <= xmin < xmax <= frame_width and 0 <= ymin < ymax <= frame_height):
            raise ValueError(f"Invalid ROI {roi}. Must be within (0,0,{frame_width},{frame_height}) as the tuple is as (xmin, ymin, xmax, ymax).")

    # Load YOLO model and perform inference
    yolo = YOLO(yolo_model)
    results = yolo.predict(frame, classes=[0], imgsz=640, verbose=False, conf=0.5, device="cpu")

    # Extract bounding boxes
    predict_boxes = results[0].boxes.xyxy.cpu()

    if predict_boxes.size(0) > 0:
        predict_boxes = predict_boxes.to(torch.float32)

        # Expand bounding boxes by 10%
        centers = (predict_boxes[:, :2] + predict_boxes[:, 2:]) / 2
        widths_heights = predict_boxes[:, 2:] - predict_boxes[:, :2]
        new_widths_heights = widths_heights * 1.1


        new_boxes = torch.zeros_like(predict_boxes)
        new_boxes[:, :2] = centers - new_widths_heights / 2
        new_boxes[:, 2:] = centers + new_widths_heights / 2


        new_boxes[:, [0, 2]] = torch.clamp(new_boxes[:, [0, 2]], min=0, max=frame_width)
        new_boxes[:, [1, 3]] = torch.clamp(new_boxes[:, [1, 3]], min=0, max=frame_height)

        new_boxes= new_boxes.numpy()

    # Filter bounding boxes based on ROI
    xmin, ymin, xmax, ymax = roi
    if predict_boxes.size(0) == 0 : #if is empty boxes
      return predict_boxes.numpy()
      filtered_boxes = []
    elif roi == None :
      return new_boxes
    else:
      filtered_boxes=[]
      for pred in new_boxes:
          pred = pred.reshape(1, -1)  # Ensure it has shape (1, 4)
          mask = ((xmin < pred[:, 0]) & (pred[:, 0] <= xmax)) | ((xmin < pred[:, 2]) & (pred[:, 2] <= xmax)) & (ymin < pred[:, 3]) & (pred[:, 3] <= ymax)
          if mask.any():  # Only append if there is at least one valid bounding box
              filtered_boxes.append(pred[mask])

      return np.concatenate(filtered_boxes, axis=0) if filtered_boxes else np.empty((0, 4), dtype=np.float32)

def action_detection(compiled_model, 
                     clip: torch.Tensor = None, 
                     bboxes: np.ndarray = None) -> np.ndarray:
    """
    Perform action detection.

    Args:
        compiled_model (torch.nn.Module or OpenVINO compiled model): The compiled model for action detection.
        clip (torch.Tensor): The input video clip tensor.
        bboxes (list or np.ndarray): Bounding boxes of detected persons.

    Returns:
        np.ndarray: Predictions from the model.
    """

    if clip is None:
        raise ValueError("Input clip must be provided.")
    if bboxes is None:
        raise ValueError("Bounding boxes must be provided.")


    if bboxes is not None:

        # Preprocessing steps
        uniform_temporal_subsample = UniformTemporalSubsample_Dict_Multi_Pathway(
            slow_pathway_num_samples=8, fast_pathway_num_samples=32, verbose=False
        )
        normalize = Normalize_Dict(mean=[123.675, 116.28, 103.53], std=[58.395, 57.12, 57.375], verbose=False)
        bbox = torch.tensor(bboxes, dtype=torch.float32).to("cpu")



        clip = clip.to(torch.float32).to("cpu")
        clip, bbox = rescale_with_boxes(clip, (320, 570), bbox)
        clip = pytorchvideo.transforms.functional.uniform_temporal_subsample(clip.cpu(), 30)
        clip, bbox = rescale_with_boxes(clip, (256, 455), bbox)
        transformed_dict = {"video": clip, "bboxes": bbox}
        transformed_dict = normalize(transformed_dict)
        transformed_dict = uniform_temporal_subsample(transformed_dict)
        clip = transformed_dict["video"]
        bbox = transformed_dict["bboxes"].to("cpu").numpy()


        if isinstance(clip, list) and len(clip) == 2:
            slow_clip = clip[0].numpy()
            fast_clip = clip[1].numpy()
        else:
            raise ValueError("Expected video to be a list containing [slow_clip, fast_clip]")

        # Ensure batch dimension
        slow_clip = np.expand_dims(slow_clip, axis=0)
        fast_clip = np.expand_dims(fast_clip, axis=0)

        inputs = {"slow_input": slow_clip, "fast_input": fast_clip, "bboxes": bbox}

        try:
            # Model inference
            with torch.no_grad():
                result = compiled_model(inputs)

        except RuntimeError as e:
            print(f"An unexpected error occurred: {str(e)}")
            raise e


        return result[0]  

    return None 