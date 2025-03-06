# SPDX-FileCopyrightText: 2025 German Aerospace Center <amiris@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0

import argparse
from enum import Enum


class ParsableEnum(Enum):
    """Extend this to create an enum that can be parsed with argparse"""

    @classmethod
    def instantiate(cls, name: str) -> Enum:
        try:
            return cls[name]
        except KeyError:
            raise argparse.ArgumentTypeError(f"'{name}' is not a valid option")

    def __str__(self):
        return self.name
