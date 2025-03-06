<!-- SPDX-FileCopyrightText: 2025 German Aerospace Center <amiris@dlr.de>

SPDX-License-Identifier: Apache-2.0 -->

# AMIRIS-PriceForecast
## _External electricity price forecasts to [AMIRIS](https://gitlab.com/dlr-ve/esy/amiris/amiris)_

[![PyPI version](https://badge.fury.io/py/amiris-priceforecast.svg)](https://badge.fury.io/py/amiris-priceforecast)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Zenodo](https://zenodo.org/badge/DOI/10.5281/zenodo.14907870.svg)](https://doi.org/10.5281/zenodo.14907870)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

AMIRIS-PriceForecast is an extension to the agent-based electricity market model [AMIRIS](https://helmholtz.software/software/amiris).
Specifically, it provides electricity price forecasts to the [`PriceForecasterApi`](https://gitlab.com/dlr-ve/esy/amiris/amiris/-/wikis/Classes/Agents/PriceForecasterApi) agent.

![amiris_ml_price_forecasting.png](docu/amiris_ml_price_forecasting.png)

## What is AMIRIS-PriceForecast?
AMIRIS-PriceForecast is a Python package designed to be used with AMIRIS. 
Specifically, it provides several time series forecasting algorithms that can be accessed via the [UrlModelService](https://gitlab.com/dlr-ve/esy/amiris/amiris/-/wikis/Classes/Util/UrlModelService).
To do this, AMIRIS-PriceForecast sets up a server and loads a user-defined forecast model.
It then waits for a [ForecastApiRequest](https://gitlab.com/dlr-ve/esy/amiris/amiris/-/wikis/Classes/Modules/ForecastApiRequest) sent by the [PriceForecasterApi](https://gitlab.com/dlr-ve/esy/amiris/amiris/-/wikis/Classes/Agents/PriceForecasterApi) agent.
After providing the forecast, which may include probabilistic forecasts, it returns a [ForecastApiResponse](https://gitlab.com/dlr-ve/esy/amiris/amiris/-/wikis/Classes/Modules/ForecastApiResponse) to the AMIRIS agent, where the simulation is resumed.

## Who is AMIRIS-PriceForecast for?
This AMIRIS extension is suitable for energy system modellers who want to extend the capabilities of the [MarketForecaster](https://gitlab.com/dlr-ve/esy/amiris/amiris/-/wikis/Classes/Agents/MarketForecaster) in AMIRIS.
The forecasting algorithms of AMIRIS-PriceForecast can vary from simple time-shifting approaches [(Hyndman, 2014)](https://robjhyndman.com/uwafiles/fpp-notes.pdf) to state-of-the-art algorithms such as Transformers [(Lim et al., 2021)](https://arxiv.org/abs/1912.09363).
However, this feature is aimed at more experienced users of AMIRIS, as it requires knowledge of the implications and limitations of forecasting in AMIRIS, as well as an understanding of the capabilities of time series forecasting techniques.
We are happy to assist you in this regard, please refer to our [Support Page](https://gitlab.com/dlr-ve/esy/amiris/amiris/-/wikis/Community/Support) for more details.

## How to use AMIRIS-PriceForecast?
See the detailed description in the [Wiki](https://gitlab.com/dlr-ve/esy/amiris/amiris/-/wikis/Extensions/PriceForecast) on setup, usage, and available forecast models of AMIRIS-PriceForecast.

## Community

As for the main AMIRIS repository, AMIRIS-PriceForecast is mainly developed by the German Aerospace Center, Institute of Networked Energy Systems.
We provide multi-level support for AMIRIS users: please see our dedicated [Support Page](https://gitlab.com/dlr-ve/esy/amiris/amiris/-/wikis/Community/Support). **We welcome all contributions**: bug reports, feature requests, and, of course, code.
Please see our [Contribution Guidelines](https://gitlab.com/dlr-ve/esy/amiris/amiris/-/wikis/Community/Contribute).

## Citing AMIRIS-PriceForecast

If you use AMIRIS-PriceForecast in an academic context please cite [doi: 10.5281/zenodo.14907870](https://doi.org/10.5281/zenodo.14907870) and [doi: 10.21105/joss.05041](https://doi.org/10.21105/joss.05041).
In other contexts, please include a link to our repositories [AMIRIS-PriceForecast](https://gitlab.com/dlr-ve/esy/amiris/extensions/priceforecast) and [AMIRIS](https://gitlab.com/dlr-ve/esy/amiris/amiris).

## Acknowledgements

The development of AMIRIS-PriceForecast was funded by the German Federal Ministry of Education and Research in the project [FEAT](https://www.dlr.de/en/ve/research-and-transfer/projects/project-feat) (01IS22073B). 
