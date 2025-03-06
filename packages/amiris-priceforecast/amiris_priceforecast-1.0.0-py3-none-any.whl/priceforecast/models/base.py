# SPDX-FileCopyrightText: 2025 German Aerospace Center <amiris@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0

import csv
from abc import ABC, abstractmethod

from fameio.time import FameTime
from pydantic import BaseModel

STEPS_PER_HOUR = 3600
ELECTRICITY_PRICE = "ElectricityPriceInEURperMWH"
RESIDUAL_LOAD = "AwardedEnergyInMWH_ResidualLoad"
ApiTimeSeries = dict[int, float]


class ForecastApiRequest(BaseModel):
    """Input for forecast API"""
    forecastStartTime: int
    forecastWindow: int
    pastTargets: ApiTimeSeries
    residualLoad: ApiTimeSeries


class ForecastApiResponse(BaseModel):
    """Output of forecast API"""
    forecastMeans: list[ApiTimeSeries]
    forecastVariances: list[ApiTimeSeries]


class RequestItem(BaseModel):
    """Data class of internally stored request"""
    date: str
    request: ForecastApiRequest


class ResponseItem(BaseModel):
    """Data class of internally stored response"""
    date: str
    response: ForecastApiResponse


class BasePredictionModel(ABC):
    _stored_requests: list[RequestItem] = []
    _stored_responses: list[ResponseItem] = []

    @staticmethod
    def _get_requested_time_steps(request: ForecastApiRequest) -> list[int]:
        """Returns all requested time steps at which forecasts are required"""
        start_time = request.forecastStartTime
        last_time = start_time + request.forecastWindow * STEPS_PER_HOUR
        return list(range(start_time, last_time, STEPS_PER_HOUR))

    @staticmethod
    def _get_sorted_by_key(series: ApiTimeSeries) -> ApiTimeSeries:
        """Returns sorted `unsorted_dict` by key"""
        return dict(sorted(series.items()))

    def fill_missing_targets(self, request: ForecastApiRequest, look_back: int) -> ApiTimeSeries:
        """Returns past_targets from `request` filled with 0 ensuring values are present for `look_back` period"""
        pattern_start_time = request.forecastStartTime - look_back * STEPS_PER_HOUR
        pattern_time_steps = list(range(pattern_start_time, request.forecastStartTime, STEPS_PER_HOUR))
        past_targets = request.pastTargets
        for step in pattern_time_steps:
            if not past_targets.get(step):
                past_targets[step] = 0
        return self._get_sorted_by_key(past_targets)

    @abstractmethod
    def forecast(self, request: ForecastApiRequest) -> ForecastApiResponse:
        """Abstract method for prediction"""
        pass

    def cast_response(self, request: ForecastApiRequest, means: list[ApiTimeSeries],
                      variances: list[ApiTimeSeries]) -> ForecastApiResponse:
        """Casts ForecastApiResponse based on given input and stores communication to internal storage"""
        response = ForecastApiResponse(forecastMeans=means, forecastVariances=variances)
        self._store(request, response)
        return response

    def _store(self, request: ForecastApiRequest, response: ForecastApiResponse) -> None:
        """
        Stores `request` and `response` as tuples with datetime string to internal list of `self._requests`
        and `self._responses`
        """
        datetime_string = FameTime.convert_fame_time_step_to_datetime(request.forecastStartTime,
                                                                      date_format="%Y-%m-%d %H:%M:%S")
        self._stored_requests.append(RequestItem(date=datetime_string, request=request))
        self._stored_responses.append(ResponseItem(date=datetime_string, response=response))

    def write_requests_and_responses(self) -> None:
        """Writes requests and responses as CSV files to disk"""
        if self._stored_requests:
            self.write_requests()
        if self._stored_responses:
            self.write_responses()

    def write_requests(self) -> None:
        """Writes Requests to CSV in format `TimeStep`, `Resolution`, N * `t_-xxxx` (past target)"""
        past_target_length = self._get_past_target_length()
        header = ["TimeStep", "StepSize"]
        header.extend([f"t_-{i:04d}" for i in reversed(range(1, past_target_length + 1))])
        with open("requests.csv", "w", newline="") as file:
            writer = csv.writer(file, delimiter=";")
            writer.writerow(header)
            for item in self._stored_requests:
                past_targets_sorted = self._get_sorted_by_key(item.request.pastTargets).values()
                writer.writerow(
                    [item.date, STEPS_PER_HOUR, *[""] * (past_target_length - len(past_targets_sorted)),
                     *past_targets_sorted])

    def _get_past_target_length(self) -> int:
        """Returns past target length extracted from length of past targets stored in last request message"""
        return len(self._stored_requests[-1].request.pastTargets)

    def write_responses(self) -> None:
        """
        Writes Responses to file `responses.csv`
        in format `TimeStep`, `Resolution`, `ForecastIndex`, `Type`, N * `t_xxxx` (forecasted target)
        """
        target_length = self._get_target_length()
        header = ["TimeStep", "StepSize", "ForecastIndex", "Type"]
        header.extend([f"t_{i:04d}" for i in range(0, target_length)])
        with open("responses.csv", "w", newline="") as file:
            writer = csv.writer(file, delimiter=";")
            writer.writerow(header)
            for item in self._stored_responses:
                for i, means in enumerate(item.response.forecastMeans):
                    means_sorted = self._get_sorted_by_key(means).values()
                    writer.writerow([item.date, STEPS_PER_HOUR, i, "means", *means_sorted])
                for j, variance in enumerate(item.response.forecastVariances):
                    vars_sorted = self._get_sorted_by_key(variance).values()
                    writer.writerow([item.date, STEPS_PER_HOUR, j, "variances", *vars_sorted])

    def _get_target_length(self) -> int:
        """Returns target length extracted from length of forecasted means stored in first response message"""
        return len(self._stored_responses[0].response.forecastMeans[0])
