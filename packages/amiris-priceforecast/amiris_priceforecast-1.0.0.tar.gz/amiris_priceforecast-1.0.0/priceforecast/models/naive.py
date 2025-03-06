# SPDX-FileCopyrightText: 2025 German Aerospace Center <amiris@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0

from priceforecast.models.base import BasePredictionModel, ForecastApiRequest, ForecastApiResponse


class StaticPredictor(BasePredictionModel):
    """Static Predictor returning '0' for all requested time steps"""

    def forecast(self, request: ForecastApiRequest) -> ForecastApiResponse:
        means = {k: 0 for k in self._get_requested_time_steps(request)}
        variances = {k: 0 for k in self._get_requested_time_steps(request)}
        return ForecastApiResponse(forecastMeans=means, forecastVariances=variances)


class TimeShiftPredictor(BasePredictionModel):
    """
    Naive forecast looking at past prices of length `SHIFT_HOURS` and re-uses these hours as forecasts assuming a
    repetitive nature of price patterns of this specified length.
    Interval is repeated until requested forecast length is reached.
    Fills missing hours with 0.
    """

    def __init__(self, shift_hours: int) -> None:
        self._shift_hours: int = shift_hours

    def forecast(self, request: ForecastApiRequest) -> ForecastApiResponse:
        past_targets = self._get_sorted_by_key(request.pastTargets)
        if len(past_targets) < self._shift_hours:
            past_targets = self.fill_missing_targets(request, look_back=self._shift_hours)
        means = [{step: list(past_targets.values())[i % self._shift_hours] for i, step in
                  enumerate(self._get_requested_time_steps(request))}]
        variances = [{k: 0 for k in self._get_requested_time_steps(request)}]
        return self.cast_response(request, means=means, variances=variances)
