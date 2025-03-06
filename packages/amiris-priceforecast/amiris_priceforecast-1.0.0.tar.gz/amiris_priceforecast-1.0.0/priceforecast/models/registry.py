# SPDX-FileCopyrightText: 2025 German Aerospace Center <amiris@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0

from enum import Enum, auto
from pathlib import Path
from typing import Callable, Union

from priceforecast.models.base import BasePredictionModel
from priceforecast.models.naive import StaticPredictor, TimeShiftPredictor
from priceforecast.models.nn.base_nn import BaseNN
from priceforecast.models.nn.config import read_config_from_path
from priceforecast.models.nn.validation import get_max_feature_lag
from priceforecast.models.util import ParsableEnum


class Models(ParsableEnum, Enum):
    Static = auto()
    TimeShift1 = auto()
    TimeShift24 = auto()
    TimeShift168 = auto()
    SimpleNN = auto()
    Transformer = auto()


def load_simple_nn(config_path: Path) -> BasePredictionModel:
    """Lazy loading of SimpleNN"""
    from priceforecast.models.nn.simple import SimpleNN
    return SimpleNN(config_path=config_path)


def load_transformer(config_path: Path) -> BasePredictionModel:
    """Lazy loading of Transformer"""
    from priceforecast.models.nn.transformer import Transformer
    config = read_config_from_path(config_path)
    return Transformer(config_path=config_path,
                       input_chunk_length=get_max_feature_lag(config),
                       output_chunk_length=config["forecast_window"],
                       n_epochs=config["epochs"],
                       **config["kwargs"],
                       )


MODEL_MAP: dict[Enum, Callable[[Path], Union[BasePredictionModel, BaseNN]]] = {
    Models.Static: lambda _: StaticPredictor(),
    Models.TimeShift1: lambda _: TimeShiftPredictor(shift_hours=1),
    Models.TimeShift24: lambda _: TimeShiftPredictor(shift_hours=24),
    Models.TimeShift168: lambda _: TimeShiftPredictor(shift_hours=168),
    Models.SimpleNN: lambda config_path: load_simple_nn(config_path=config_path),
    Models.Transformer: lambda config_path: load_transformer(config_path=config_path),
}
