# SPDX-FileCopyrightText: 2025 German Aerospace Center <amiris@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0

import logging as log

ERR_MISSING_LAG_DEFINITION = "Missing required definition '{}' in given config."
ERR_TIME_SERIES_SHORT = "Given time_series is too short for specified lags and forecast horizon."
ERR_INVALID_PAST_LAGS = ("Received invalid past lags for column_name '{}'. "
                         "Make sure you provide a list of strictly positive integers with each element > 0.")
ERR_INVALID_FUTURE_LAGS = ("Received invalid future lags for column_name '{}'. "
                           "Make sure you provide a list of strictly positive integers with each element >= 0.")
ERR_NOT_FUTURE_LAGS_FOR_TARGET = ("Received illegal future lags for column_name '{}' which is also specified as target."
                                  "Either remove future lags or remove this column_name from target(s)")
ERR_INVALID_HORIZON = "Received invalid forecast horizon. Make sure to provide an integer >= 1."
WARN_REMOVED_ILLEGAL_PAST_LAGS = "Removed illegal 'past_lags'  for target with column name '{}'."

WARN_REPLACED_FUTURE_LAGS = ("Given `future_lags` for target '{}' were ignored. "
                             "Applied `{} future_lags` starting at `0` instead.")


def validate_config(config: dict) -> dict:
    """Returns validated `config`"""
    check_forecast_window(config["forecast_window"])
    return validate_lags(config)


def get_target_names(target_definitions: [dict]) -> list[str]:
    """Returns extracted target column names from given `target_definitions`"""
    return [item["column_name"] for item in target_definitions]


def check_past_lags(item: dict) -> None:
    """Raises ValueError if given past_lags in `item` are not valid"""
    lags = item["past_lags"]
    column_name = item["column_name"]
    if lags:
        if not isinstance(lags, list):
            raise ValueError(ERR_INVALID_PAST_LAGS.format(column_name))
        if any(not isinstance(x, int) for x in lags):
            raise ValueError(ERR_INVALID_PAST_LAGS.format(column_name))
        if min(lags) <= 0:
            raise ValueError(ERR_INVALID_PAST_LAGS.format(column_name))


def check_future_lags(item: dict, target_names: list[str]) -> None:
    """Raises ValueError if given future_lags in `item` are not valid also considering `target_names`"""
    lags = item["future_lags"]
    column_name = item["column_name"]
    if lags:
        if not isinstance(lags, list):
            raise ValueError(ERR_INVALID_FUTURE_LAGS.format(column_name))
        if any(not isinstance(x, int) for x in lags):
            raise ValueError(ERR_INVALID_FUTURE_LAGS.format(column_name))
        if min(lags) < 0:
            raise ValueError(ERR_INVALID_FUTURE_LAGS.format(column_name))
        if column_name in target_names:
            raise ValueError(ERR_NOT_FUTURE_LAGS_FOR_TARGET.format(column_name))


def validate_lags(config: dict) -> dict:
    """Raises ValueError if `lags` are not a strictly positive list of integers"""
    raise_if_lag_definition_missing(config)
    validate_features(config)
    validate_targets(config)
    return config


def validate_features(config: dict) -> None:
    """Validates features by checking their individual future and past lags for validity"""
    for feature in config["features"]:
        if "past_lags" in feature:
            check_past_lags(feature)
        if "future_lags" in feature:
            check_future_lags(feature, get_target_names(config["targets"]))


def validate_targets(config: dict) -> None:
    """Validates targets by removing potential past_lags and adding future_lags in length of forecat_window"""
    for target in config["targets"]:
        if "past_lags" in target:
            log.warning(WARN_REMOVED_ILLEGAL_PAST_LAGS.format(target["column_name"]))
            target.pop("past_lags")
        if target.get("future_lags"):
            log.warning(WARN_REPLACED_FUTURE_LAGS.format(target['column_name'], config["forecast_window"]))
        target["future_lags"] = [i for i in range(0, config["forecast_window"])]


def raise_if_lag_definition_missing(config: dict) -> None:
    """Raises KeyError if `targets` or `features` are missing in `config`"""
    for check in ["targets", "features"]:
        if check not in config:
            raise KeyError(ERR_MISSING_LAG_DEFINITION.format(check))


def check_forecast_window(forecast_horizon: int) -> None:
    """Raises ValueError `forecast_horizon` is not a positive integer >= 1"""
    if not isinstance(forecast_horizon, int):
        raise ValueError(ERR_INVALID_HORIZON)
    if forecast_horizon <= 0:
        raise ValueError(ERR_INVALID_HORIZON)


def get_max_feature_lag(config: dict) -> int:
    """Returns max lag as specified in `config`"""
    max_lag = 0
    for lag_definition in config["features"]:
        if "past_lags" in lag_definition and lag_definition["past_lags"]:
            max_lag = max(max_lag, max(lag_definition["past_lags"]))
        if "future_lags" in lag_definition and lag_definition["future_lags"]:
            max_lag = max(max_lag, max(lag_definition["future_lags"]))
    return max_lag


def get_max_past_feature_lag(features: dict) -> int:
    """Returns max `past_lags` from `features`"""
    max_past_feature_lag = 0
    for feature in features:
        max_past_feature_lag = max(max(feature.get("past_lags", [0])), max_past_feature_lag)
    return max_past_feature_lag
