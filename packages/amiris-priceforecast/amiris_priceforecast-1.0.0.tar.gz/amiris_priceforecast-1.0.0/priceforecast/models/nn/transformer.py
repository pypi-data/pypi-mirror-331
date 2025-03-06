# SPDX-FileCopyrightText: 2025 German Aerospace Center <amiris@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0

import logging as log
from pathlib import Path
from typing import Union, Optional

import pandas as pd
from fameio.tools import ensure_path_exists
from torch import nn
from darts import TimeSeries, concatenate
from darts.models import TFTModel
from darts.utils.likelihood_models import Likelihood

from priceforecast.logs import log_and_raise_critical
from priceforecast.models.base import ForecastApiRequest, ForecastApiResponse, ELECTRICITY_PRICE, RESIDUAL_LOAD, \
    ApiTimeSeries
from priceforecast.models.nn.base_nn import BaseNN, WEIGHTS_KEY
from priceforecast.models.nn.data_preparation import get_features_with_lags
from priceforecast.models.nn.validation import get_max_past_feature_lag

ERR_INVALID_CONFIG = ("Error when loading weights from {} Ensure that all `kwargs` are identical as used in training.\n"
                      "Traceback: {}")
DBG_PREDICTION_X_STEPS_AT_Y = "Predicting {} timesteps starting at {}"
ERR_NO_MATCH_FOR_COV = "Could not match given column_name '{}' to possible matches '{}' for specified '{}'."


class Transformer(TFTModel, BaseNN):
    """
    Class that implements a Temporal Fusion Transformer, https://doi.org/10.1016/j.ijforecast.2021.03.012

    Note:
        Since the darts constructor collects the top-level init args, they have to be explicitly stated here,
        although they could also be extracted in this init from the config, as in all other NN implementations.
    """

    def __init__(self,
                 config_path: Path,
                 input_chunk_length: int,
                 output_chunk_length: int,
                 n_epochs: int,
                 # necessary to state explicitly here, otherwise darts constructor fails
                 output_chunk_shift: int = 0,
                 hidden_size: Union[int, list[int]] = 16,
                 lstm_layers: int = 1,
                 num_attention_heads: int = 4,
                 full_attention: bool = False,
                 feed_forward: str = "GatedResidualNetwork",
                 dropout: float = 0.1,
                 hidden_continuous_size: int = 8,
                 categorical_embedding_sizes: Optional[dict[str, Union[int, tuple[int, int]]]] = None,
                 add_relative_index: bool = False,
                 loss_fn: Optional[nn.Module] = None,
                 likelihood: Optional[Likelihood] = None,
                 norm_type: Union[str, nn.Module] = "LayerNorm",
                 use_static_covariates: bool = True,
                 **kwargs
                 ):
        BaseNN.__init__(self, config_path)
        TFTModel.__init__(self,
                          input_chunk_length=input_chunk_length,
                          output_chunk_length=output_chunk_length,
                          n_epochs=n_epochs,
                          output_chunk_shift=output_chunk_shift,
                          hidden_size=hidden_size,
                          lstm_layers=lstm_layers,
                          num_attention_heads=num_attention_heads,
                          full_attention=full_attention,
                          feed_forward=feed_forward,
                          dropout=dropout,
                          hidden_continuous_size=hidden_continuous_size,
                          categorical_embedding_sizes=categorical_embedding_sizes,
                          add_relative_index=add_relative_index,
                          loss_fn=loss_fn,
                          likelihood=likelihood,
                          norm_type=norm_type,
                          use_static_covariates=use_static_covariates,
                          **kwargs,
                          )
        if self.config.get(WEIGHTS_KEY):
            log.debug(f"Loading weights from {self.config[WEIGHTS_KEY]}")
            try:
                self.load_weights(self.config[WEIGHTS_KEY], skip_checks=True, load_encoders=False)
            except RuntimeError as e:
                log_and_raise_critical(ERR_INVALID_CONFIG.format(self.config[WEIGHTS_KEY], e))
        log.getLogger("pytorch_lightning").setLevel(log.WARNING)

    def forecast(self, request: ForecastApiRequest) -> ForecastApiResponse:
        """Return `ForecastApiResponse` on given `request`"""
        past_targets = self._get_sorted_by_key(request.pastTargets)
        max_lags = get_max_past_feature_lag(self.config["features"])
        if len(past_targets) < max_lags:
            past_targets = self.fill_missing_targets(request, look_back=max_lags)

        past_covariates = self.prepare_covariates(past_targets, request, "past_lags", is_future=False)
        future_covariates = self.prepare_covariates(past_targets, request, "future_lags", is_future=True)

        args = {"n": request.forecastWindow,
                "series": self.convert_to_timeseries(past_targets),
                "future_covariates": None if not future_covariates else concatenate(future_covariates, axis=1),
                "past_covariates": None if not past_covariates else concatenate(past_covariates, axis=1),
                }

        prediction = self.predict(**args, verbose=0, num_samples=self.num_of_forecasts)
        means = []
        for col in prediction.pd_dataframe():
            means.append(dict(zip(self._get_requested_time_steps(request), prediction.pd_dataframe()[col].values)))
        if self.num_of_forecasts > 1:
            variances = [dict(zip(self._get_requested_time_steps(request), prediction.skew().univariate_values()))]
        else:
            variances = [{k: 0 for k in self._get_requested_time_steps(request)}]
        return self.cast_response(request, means=means, variances=variances)

    def prepare_covariates(self, past_targets: ApiTimeSeries, request: ForecastApiRequest, lag_type: str,
                           is_future: bool = False) -> list[TimeSeries]:
        """Helper function to prepare covariates for past or future lags"""
        covariates = []
        lag_columns = get_features_with_lags(self.config, lag_type)
        for column_name in lag_columns:
            if column_name == ELECTRICITY_PRICE:
                covariates.append(self.convert_to_timeseries(past_targets))
            elif column_name == RESIDUAL_LOAD:
                data = request.residualLoad if is_future else self.get_data_before(request.residualLoad,
                                                                                   before=request.forecastStartTime)
                covariates.append(self.convert_to_timeseries(data))
            else:
                raise ValueError(ERR_NO_MATCH_FOR_COV.format(column_name, [ELECTRICITY_PRICE, RESIDUAL_LOAD], lag_type))
        return covariates

    @staticmethod
    def convert_to_timeseries(input_raw: ApiTimeSeries) -> TimeSeries:
        """Returns `input_raw` for selected `column_names` in required format"""
        input_raw = pd.DataFrame.from_dict(input_raw, orient="index")
        return TimeSeries.from_dataframe(input_raw)

    def get_data_before(self, data: ApiTimeSeries, before: int) -> ApiTimeSeries:
        """Splits given `data` to only store values before `split_point`"""
        past_data = {}
        for time_step, value in self._get_sorted_by_key(data).items():
            if time_step < before:
                past_data[time_step] = value
        return past_data

    def train_nn(self, data: dict[str, pd.DataFrame]) -> None:
        """Trains the Transformer Network"""
        args = {"series": self.prepare_train_data(data, [target["column_name"] for target in self.config["targets"]])}
        future_covs = get_features_with_lags(self.config, "future_lags")
        if future_covs:
            args["future_covariates"] = self.prepare_train_data(data, future_covs)
        past_covs = get_features_with_lags(self.config, "past_lags")
        if past_covs:
            args["past_covariates"] = self.prepare_train_data(data, past_covs)
        self.fit(**args)

    @staticmethod
    def prepare_train_data(train_raw: dict[str, pd.DataFrame], column_names: list[str]) -> list[TimeSeries]:
        """Returns `train_raw` for selected `column_names` in required format for training"""
        compiled = []
        for _, values in train_raw.items():
            compiled.append(TimeSeries.from_dataframe(values[column_names]))
        return compiled

    def write_weights_to_disk(self, path: Path) -> None:
        """Writes weights to disk in `path`"""
        ensure_path_exists(path.parent)
        self.save(path.as_posix())
