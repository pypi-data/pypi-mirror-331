# SPDX-FileCopyrightText: 2025 German Aerospace Center <amiris@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0

import logging as log
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from priceforecast.models.base import ForecastApiRequest, ForecastApiResponse
from priceforecast.models.nn.base_nn import BaseNN, NNDataset, WEIGHTS_KEY
from priceforecast.models.nn.data_preparation import create_features_and_targets


class SimpleNN(BaseNN):
    """Class that implements a very simple neural network model."""

    def __init__(self, config_path: Path):
        super(SimpleNN, self).__init__(config_path)
        self.forecast_window = self.config['forecast_window']
        self.features = self.config['features']
        self.targets = self.config['targets']
        self.seq_len = self.get_seq_len()
        self.hidden_units = self.config['hidden_units']

        self.fc1 = torch.nn.Linear(self.seq_len, self.hidden_units)
        self.fc2 = torch.nn.Linear(self.hidden_units, self.hidden_units)
        self.fc4 = torch.nn.Linear(self.hidden_units, self.forecast_window)
        if self.config.get(WEIGHTS_KEY):
            log.debug(f"Loading weights from {self.config[WEIGHTS_KEY]}")
            self.load_state_dict(torch.load(self.config[WEIGHTS_KEY], weights_only=False), strict=False)

    def get_seq_len(self) -> int:
        """Returns sequence length based on counted 'future_lags' and 'past_lags'"""
        count = 0
        for feature in self.config["features"]:
            count += len(feature.get("future_lags", [])) + len(feature.get("past_lags", []))
        return count

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Receives Tensor `x` [Batch, Input length] and returns processed Tensor `x` [Batch, Output length]"""
        x = self.fc1(x)
        x = torch.nn.functional.relu(x)
        x = self.fc2(x)
        x = torch.nn.functional.relu(x)
        x = self.fc4(x)
        return x

    def forecast(self, request: ForecastApiRequest) -> ForecastApiResponse:
        """Return `ForecastApiResponse` on given `request`"""
        past_targets = self._get_sorted_by_key(request.pastTargets)
        if len(past_targets) < max(self.features):
            past_targets = self.fill_missing_targets(request, look_back=max(self.features))
        features = np.array(list(past_targets.values()))[[-lag for lag in self.features]]
        output = self.forward(torch.Tensor(features[None, :])).detach().numpy()[0]
        means = [dict(zip(self._get_requested_time_steps(request), list(output)))]
        variances = [{k: 0 for k in self._get_requested_time_steps(request)}]
        return self.cast_response(request, means=means, variances=variances)

    def create_dataset(self, data: dict[str, pd.DataFrame]) -> NNDataset:
        """
        Converts input data into the form required for training (input features and output targets).

        Args:
            data: dict of scenarios and corresponding timeseries (as defined in FeatWrapper Processor)
        """
        features, targets = create_features_and_targets(data,
                                                        feature_definitions=self.features,
                                                        target_definitions=self.targets)
        return NNDataset(features=torch.Tensor(features.to_numpy()), targets=torch.Tensor(targets.to_numpy()))

    def train_nn(self, data: dict[str, pd.DataFrame]) -> None:
        """
        Trains a NN to predict targets based on features.

        Args:
            data: dictionary of scenarios to be used for training
        """
        training_data = self.create_dataset(data)
        train_dataloader = torch.utils.data.DataLoader(training_data, batch_size=self.config["batch_size"],
                                                       shuffle=True)
        optimizer = torch.optim.Adam(
            self.parameters(),
            lr=self.config["learning_rate"],
            weight_decay=self.config["weight_decay"])
        loss = torch.nn.MSELoss()

        for epoch in range(self.config["epochs"]):
            epoch_loss = 0.0
            num_batches = 0

            for features, targets in train_dataloader:
                prediction = self.forward(features)
                loss_val = loss(prediction, targets)
                optimizer.zero_grad()
                loss_val.backward()
                optimizer.step()
                epoch_loss += loss_val.item()
                num_batches += 1

            avg_loss = epoch_loss / num_batches
            if epoch % 10 == 0:
                print(f"Epoch {epoch}/{self.config['epochs']} - Loss: {avg_loss:.4f}")
