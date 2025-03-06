# SPDX-FileCopyrightText: 2025 German Aerospace Center <amiris@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path

import yaml
from priceforecast.logs import log_and_raise_critical
from priceforecast.models.nn.validation import validate_config


def read_config_from_path(config_path: Path) -> dict:
    """Returns parsed config from given `config_path`"""
    if config_path is None:
        log_and_raise_critical("Your requested model requires a `--config_path / -cp`, but received 'None'")
    with open(config_path, 'r') as file:
        config = validate_config(yaml.safe_load(file))
    return config
