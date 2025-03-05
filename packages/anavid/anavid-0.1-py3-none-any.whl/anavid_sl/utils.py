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

class UniformTemporalSubsample_Dict_Multi_Pathway(torch.nn.Module):
    def __init__(self, slow_pathway_num_samples: int, fast_pathway_num_samples: int, temporal_dim: int = -3, verbose: bool = False):
        super().__init__()
        self.slow_pathway_num_samples = slow_pathway_num_samples
        self.fast_pathway_num_samples = fast_pathway_num_samples
        self._temporal_dim = temporal_dim
        self.verbose = verbose

    def forward(self, input_dict: Dict) -> Dict:
        input_tensor = input_dict['video'].cpu()

        slow_sampled_video = pytorchvideo.transforms.functional.uniform_temporal_subsample(
            input_tensor, self.slow_pathway_num_samples, self._temporal_dim
        )
        fast_sampled_video = pytorchvideo.transforms.functional.uniform_temporal_subsample(
            input_tensor, self.fast_pathway_num_samples, self._temporal_dim
        )

        output_dict = {
            'video': [slow_sampled_video, fast_sampled_video],
            'bboxes': input_dict['bboxes']
        }
        return output_dict
def rescale_with_boxes(images: torch.Tensor,size: Tuple[int,int] ,boxes : torch.Tensor,interpolation: str = "bilinear",backend: str = "pytorch",verbose: bool = False) -> torch.Tensor:
        
        """
        Rescale an input tensor and its associated bounding boxes.

        Parameters:
        - x (torch.Tensor): Input tensor to be rescaled. It should have shape (batch_size, channels, height, width).
        - size (tuple[int, int]): Output size after rescaling, specified as (height, width).
        - bboxes (torch.Tensor): Bounding boxes associated with the input tensor.
                                Each row represents a box in the format (x_min, y_min, x_max, y_max).
        - interpolation (str, optional): Interpolation method for rescaling. Default is "bilinear".
        - backend (str, optional): Rescaling backend. Default is "pytorch".

        Returns:
        - torch.Tensor: Rescaled tensor with shape (n_frames, channels, size[0], size[1]).
        - torch.Tensor: Modified bounding boxes corresponding to the rescaled tensor.
                    Each row represents a box in the format (x_min, y_min, x_max, y_max).

        Note:
        - The input bounding boxes are modified to match the rescaled dimensions.
        - Supported interpolation methods: "nearest", "bilinear", "bicubic", "area".
        - Supported backends: "pytorch", "opencv".
        """
        # noqa
        x_rescale_ratio = size[1] /  images.shape[3] 
        y_rescale_ratio = size[0]/ images.shape[2] 


        rescaled_imgs = rescale(images, size, interpolation, backend)

        # Create a new tensor for modified bounding boxes
        rescaled_bboxes = boxes.clone()
        if len(rescaled_bboxes.shape) == 3:
            rescaled_bboxes = rescaled_bboxes[0]
        # Modify bounding boxes
        rescaled_bboxes[:, 0] *= x_rescale_ratio
        rescaled_bboxes[:, 2] *= x_rescale_ratio
        rescaled_bboxes[:, 1] *= y_rescale_ratio
        rescaled_bboxes[:, 3] *= y_rescale_ratio

        
        if verbose:
            print(f'-- size changed from: ({images.shape[2]} ,{images.shape[3]}) ---> ({size[0]} ,{size[1]})')
            print('-- x_rescale_ratio', x_rescale_ratio)
            print('-- y_rescale_ratio', y_rescale_ratio)
            print('-- Rescaled box', rescaled_bboxes)

        return rescaled_imgs, rescaled_bboxes


def rescale(x: torch.Tensor,size: Tuple[int,int] ,interpolation: str = "bilinear",backend: str = "pytorch") -> torch.Tensor:
        """
        Rescales a 4D torch.Tensor representing an image or a batch of images.

        Parameters:
        - x (torch.Tensor): Input tensor of shape (C, T, H, W), where C is the number of channels,
                        T is the number of frames, and H, W are the height and width of each frame.
        - size (tuple[int, int]): The target size (height, width) for the rescaled images.
        - interpolation (str, optional): Interpolation method for resizing. Default is "bilinear".
        - backend (str, optional): The backend to use for interpolation, either "pytorch" or "opencv".
                                Default is "pytorch".

        Returns:
        - torch.Tensor: Rescaled tensor of shape (C, T, size[0], size[1]).

        Note:
        - If backend is "pytorch", uses torch.nn.functional.interpolate for resizing.
        - If backend is "opencv", uses a custom function _interpolate_opencv.
        """
        assert len(x.shape) == 4
        assert x.dtype == torch.float32
        assert backend in ("pytorch", "opencv")
        if backend == "pytorch":
            return torch.nn.functional.interpolate(
                x, size=(size[0], size[1]), mode=interpolation, align_corners=False
            )
        elif backend == "opencv":
            return _interpolate_opencv(x, size=(size[0], size[1]), interpolation=interpolation)
        else:
            raise NotImplementedError(f"{backend} backend not supported.")


class Normalize_Dict(torchvision.transforms.Normalize):
    def __init__(self, mean, std, verbose: bool = False) -> None:
        super().__init__(mean, std)
        self.verbose = verbose

    def forward(self, input_dict: Dict) -> Dict:
        if isinstance(input_dict['video'], torch.Tensor):
            vid = input_dict['video'].permute(1, 0, 2, 3)
            vid = super().forward(vid)
            vid = vid.permute(1, 0, 2, 3)
            output_vid = vid
        elif isinstance(input_dict['video'], list):
            output_vid = []
            for vid in input_dict['video']:
                vid = vid.detach().permute(1, 0, 2, 3)
                vid = super().forward(vid)
                vid = vid.permute(1, 0, 2, 3)
                output_vid.append(vid)
        
        output_dict = {'video': output_vid, 'bboxes': input_dict['bboxes']}
        return output_dict



def to_tensor(img):
        img = torch.from_numpy(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        return img.unsqueeze(0) 

def get_video_clip(stack):
        assert len(stack) > 0, "clip length must large than 0 !"
        
        stack = [to_tensor(img) for img in stack]
        clip = torch.cat(stack).permute(-1, 0, 1, 2)
        del stack
        stack = []
        return clip   