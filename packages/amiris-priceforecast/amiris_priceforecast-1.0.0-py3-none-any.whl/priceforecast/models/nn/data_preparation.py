# SPDX-FileCopyrightText: 2025 German Aerospace Center <amiris@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0

import pandas as pd

TARGET_IDENTIFIER = "$T$_"


def lag_columns(df: pd.DataFrame, lag_definition: dict, is_target: bool = False) -> pd.DataFrame():
    """
    Lags column(s) in `df` with lag(s) as defined in `lag_definition`
    Appends `target_identifier` in front of target columns (identified by `is_target`)

    Note:
        `pd.shift()` interprets negative lags as future features
        lag = 0 is the first value to be forecasted, lag = -1 is the most recent past value

    Args:
        df: Single DataFrame which is used to lag columns
        lag_definition: specifies lag definition, e.g. column_name, future_lags, past_lags
        is_target: if column is target, a prefix is added to column_name for identification

    Returns:
        DataFrame with lagged columns
    """
    past_lags = lag_definition.get("past_lags", [])
    future_lags = lag_definition.get("future_lags", [])
    lags = sorted([*[i * -1 if i > 0 else i for i in future_lags], *past_lags])
    target_prefix = TARGET_IDENTIFIER if is_target else ""
    column_name = lag_definition["column_name"]
    df = df.assign(**{
        f'{target_prefix}{column_name}_{lag}': df[column_name].shift(lag)
        for lag in lags
    })
    return df


def create_features_and_targets(data: dict[str, pd.DataFrame], feature_definitions: list[dict],
                                target_definitions: list[dict]) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Creates lagged features and targets from given `data` according to `feature_definitions` and `target_definitions`

    Args:
        data: Data from which features and targets should be derived from
        feature_definitions: specifications of feature(s) (e.g., column_name, future_lags, past_lags)
        target_definitions: specifications of target(s) (e.g., column_name)

    Returns:
        Two pd.DataFrames of features and targets which can be used for training
    """

    feature_columns = [item["column_name"] for item in feature_definitions]
    target_columns = [item["column_name"] for item in target_definitions]
    lagged_data = []
    for _, scenario_data in data.items():
        original_columns = list({*feature_columns, *target_columns})
        scenario_data = scenario_data[original_columns]
        for feature_lag_definition in feature_definitions:
            scenario_data = lag_columns(scenario_data, feature_lag_definition)
        for target_lag_definition in target_definitions:
            scenario_data = lag_columns(scenario_data, target_lag_definition, is_target=True)
        lagged_data.append(scenario_data.drop(columns=original_columns))
    combined = pd.concat(lagged_data).dropna()
    features = combined[[c for c in combined.columns if TARGET_IDENTIFIER not in c]]
    targets = combined[[c for c in combined.columns if TARGET_IDENTIFIER in c]]
    return features, targets


def get_features_with_lags(config: dict, lag_type: str) -> list[str]:
    """Returns list of column names from features where `lag_type` is greater 0"""
    return [feature["column_name"] for feature in config["features"] if len(feature.get(lag_type, [])) > 0]
