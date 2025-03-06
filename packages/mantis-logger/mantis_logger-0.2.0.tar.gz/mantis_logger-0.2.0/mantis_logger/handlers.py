#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2016-2024 AMOSSYS
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
import inspect
import logging
import traceback
from typing import Any
from typing import Dict
from typing import Optional

from loguru import logger
from loki_logger_handler.loki_logger_handler import LoguruFormatter
from loki_logger_handler.loki_logger_handler import LokiLoggerHandler

from .config import mantis_logger_config


# This class is here because the loki_logger_handler.loki_logger_handle.LoguruFormatter clas suses
# python 3.9 operators (even though it says it works with python 3.6)
class _LoguruFormatterOverloadedFromLokiLoggerHandler(LoguruFormatter):
    def format(self, record):
        formatted = {
            "message": record.get("message"),
            "timestamp": record.get("time").timestamp(),
            "process": record.get("process").id,
            "thread": record.get("thread").id,
            "function": record.get("function"),
            "module": record.get("module"),
            "name": record.get("name"),
            "level": record.get("level").name,
        }

        if record.get("extra"):
            if record.get("extra").get("extra"):
                formatted.update(record.get("extra").get("extra"))
            else:
                formatted.update(record.get("extra"))

        if record.get("level").name == "ERROR":
            formatted["file"] = record.get("file").name
            formatted["path"] = record.get("file").path
            formatted["line"] = record.get("line")

            if record.get("exception"):
                exc_type, exc_value, exc_traceback = record.get("exception")
                formatted_traceback = traceback.format_exception(
                    exc_type, exc_value, exc_traceback
                )
                formatted["stacktrace"] = "".join(formatted_traceback)

        return formatted


class CentralizedLoggerHandler(LokiLoggerHandler):
    def __init__(
        self,
        labels: Optional[Dict[str, str]],
    ) -> None:
        super().__init__(
            url=mantis_logger_config.loki_url,
            labels=labels,
            defaultFormatter=_LoguruFormatterOverloadedFromLokiLoggerHandler(),
        )


class InterceptHandler(logging.Handler):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        # Since this can be called as a init of StreamHandler, there will be gargabe args/kwargs.
        # We only take the level
        level = logging.NOTSET
        if "level" in kwargs:
            level = kwargs["level"]
        super().__init__(level)

    # To simulate a valid StreamHandler
    def setStream(self, stream: Any) -> None:
        pass

    def emit(self, record: logging.LogRecord) -> None:
        # Get corresponding Loguru level if it exists.
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message.
        frame, depth = inspect.currentframe(), 0
        while frame and (depth == 0 or frame.f_code.co_filename == logging.__file__):
            frame = frame.f_back
            depth += 1

        effective_logger = logger.bind(name=record.name)
        formatted_message = record.getMessage()

        effective_logger.opt(depth=depth, exception=record.exc_info).log(
            level, formatted_message
        )
