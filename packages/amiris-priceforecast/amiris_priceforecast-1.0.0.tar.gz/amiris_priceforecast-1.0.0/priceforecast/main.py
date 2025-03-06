# SPDX-FileCopyrightText: 2025 German Aerospace Center <amiris@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0

import logging
from typing import Optional, Callable

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from priceforecast.cli import arg_handling_run, GeneralOptions, Command, RunOptions
from priceforecast.logs import set_up_logger, log_and_print

from priceforecast.models.base import ForecastApiRequest, ForecastApiResponse
from priceforecast.models.registry import BasePredictionModel, MODEL_MAP

WELCOME_MSG = (
    "<html><body>Welcome to AMIRIS-PriceForecast - an extension to the agent-based electricity market model AMIRIS"
    "Please check the <a href='/docs'>documentation</a></body></html>"
)


class PriceForecastServer:
    """Price Forecast Server"""

    def __init__(self, callback: Callable = None):
        self.app = FastAPI()
        self._prediction_model = None
        self.server = None
        self._callback = callback
        self._setup_routes()

    def _setup_routes(self):
        """Registers available routes"""
        self.app.get("/", response_class=HTMLResponse)(self._root)
        self.app.post("/forecast")(self._forecast)
        self.app.post("/shutdown")(self._shutdown)

    @staticmethod
    async def _root() -> str:
        """Returns welcome message"""
        return WELCOME_MSG

    async def _forecast(self, request: ForecastApiRequest) -> ForecastApiResponse:
        """Returns ForecastApiResponse based on ForecastApiRequest, raises HTTPException if no model set"""
        if self._prediction_model is None:
            raise HTTPException(status_code=500, detail="Model not set")
        return self._prediction_model.forecast(request)

    async def _shutdown(self) -> HTMLResponse:
        """Gracefully shuts down the server"""
        if self.server:
            self.server.should_exit = True
        return HTMLResponse(content="Shutting down...", status_code=200)

    def run(self, host: str, port: int, log_level: str):
        """Runs the FastAPI server on given `host`, `port` and `log_level`"""
        self.server = uvicorn.Server(uvicorn.Config(self.app, host=host, port=port, log_level=log_level.lower()))
        if self._callback:
            self._callback()
            logging.debug("Triggered callback")
        self.server.run()

    def set_model(self, model: BasePredictionModel) -> None:
        """Sets the prediction model"""
        self._prediction_model = model

    @property
    def prediction_model(self):
        """Gets the current prediction model"""
        return self._prediction_model


def priceforecast_cli(args: Optional[list[str]] = None, callback: Optional[callable] = None) -> None:
    """Calls sub-commands with appropriate arguments from the command line parser."""
    command, options = arg_handling_run(args)
    set_up_logger(options[GeneralOptions.LOG], options[GeneralOptions.LOGFILE])
    log_and_print("Starting AMIRIS-PriceForecast")

    if command is Command.RUN:
        prediction_model = MODEL_MAP[options[RunOptions.MODEL]](options.get(RunOptions.CONFIG_PATH))
        api_server = PriceForecastServer(callback)
        api_server.set_model(prediction_model)
        api_server.run(options[RunOptions.HOST], options[RunOptions.PORT], options[GeneralOptions.LOG])
        if RunOptions.LOG_COMMUNICATION:
            prediction_model.write_requests_and_responses()


if __name__ == "__main__":
    priceforecast_cli()
