# SPDX-FileCopyrightText: 2025 German Aerospace Center <amiris@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0

from abc import ABC, abstractmethod
from pathlib import Path

import pandas as pd

import torch
from fameio.tools import ensure_path_exists
from priceforecast.models.nn.config import read_config_from_path
from torch.utils.data import Dataset

from priceforecast.models.base import BasePredictionModel

WEIGHTS_KEY = "checkpoint"


class BaseNN(BasePredictionModel, ABC, torch.nn.Module):
    """Base Model for torch neural network models"""

    def __init__(self, config_path: Path):
        super(BaseNN, self).__init__()
        self.config: dict = read_config_from_path(config_path)
        self.num_of_forecasts: int = self.config.get("n_forecast", 1)

    @abstractmethod
    def train_nn(self, data: dict[str, pd.DataFrame]) -> None:
        """Abstract method for training"""
        pass

    def write_weights_to_disk(self, path: Path) -> None:
        """Writes weights to disk in `path`"""
        ensure_path_exists(path.parent)
        with open(path, "wb") as file:
            torch.save(self.state_dict(), file)


class NNDataset(Dataset):
    """Dataset of torch neural networks hosting features and targets"""

    def __init__(self, features: torch.Tensor, targets: torch.Tensor) -> None:
        self.features = features
        self.targets = targets

    def __len__(self) -> int:
        """Returns the length of the target Tensor"""
        return len(self.targets)

    def __getitem__(self, idx: int) -> tuple[torch.Tensor, torch.Tensor]:
        """Returns the Feature Tensor and Target Tensor at position `idx`"""
        return self.features[idx], self.targets[idx]
