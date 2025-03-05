import sys

import torch

from bkit.shallow import dataloaders

sys.modules["dataloaders"] = dataloaders

use_cuda = torch.cuda.is_available()

if use_cuda:
    torch_t = torch.cuda

    def from_numpy(ndarray):
        return torch.from_numpy(ndarray).pin_memory().cuda(non_blocking=False)

else:
    torch_t = torch
    from torch import from_numpy


# Function to load a PyTorch model from a file path
def torch_load(load_path):
    if use_cuda:
        return torch.load(load_path)
    else:
        return torch.load(load_path, map_location=lambda storage, location: storage)
