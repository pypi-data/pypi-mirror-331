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
import logging.config
import sys
from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional

import loguru._defaults
from loguru import logger  # noqa: F401

from .config import mantis_logger_config
from .handlers import CentralizedLoggerHandler
from .handlers import InterceptHandler


def configure(
    *,
    loki_labels: Optional[Dict[str, str]] = None,
    force_no_loki: bool = False,
    loguru_outputs_handlers: Optional[List[Dict[str, Any]]] = None,
    main_logger_level: Optional[str] = None,
    main_logger_print_files_and_lines: bool = True,
    component_specific_loggers_config: Optional[Dict[str, Dict[str, Any]]] = None,
    **kwargs,
) -> None:
    """
    Configures the interception, format, and filters of logs of a component, and the sending of a copy to Loki.

    Typically called at the start of a component.

    It intercepts logs, and (by default) prints them to stderr, and sends a copy to a Loki instance.

    The architecture of loggers, after configuration through this function, can be seen as an hourglass:
    * Upper part of the hourglass : we intercept a lot (not *everything*, we do not necessary care
    about debug logs of e.g. sqlalchemy)
         * We intercept standard python loggers by greatly modifying the configuration of the `logging` package.
         * We "intercept" Loguru loggers natively
    * Neck of the hourglass : all ends up in loguru
    * Bottom of the hourglass : dispatching (i.e. configure loguru "sinks")
        * We forward everything we capture to Loki (if a Loki URL is configured)
        * We print to stderr all messages above a configurable level (with potential formatters)
            * Optionally, the user can define its own "sink" to print to stderr or files, or anything

    **Interception explained in details**

    Interception is done only for loguru and python standard logging. Other logging libs are not
    handled as of today.

    The "interception" of loguru logs is not an interception : if a component or a component's
    library directly uses loguru, then the logs will directly go to loguru, which is what we want.

    To intercept standard python loggers (module `logging`), we do the following:
    * allow the user of this function, through component_specific_loggers_config, to configure
      python standard loggers for interception. All loggers specified by the user are reconfigured
      to have the level specified by the user (or one by default), and only 1 handler: an
      InterceptHandler of our own.
       * Note : this discards all handlers, filters and formatters that may pre-exist for these
          standard python loggers
    * Set the root logger at level NOSET, and discard its handlers, to place only one handler (an
      InterceptHandler)
    * Overload the `logging.lastResort` handler with an InterceptHandler of our own. This lastResort
      is used on a log record only when no other handler in the stack of loggers has handled them.

    The InterceptHandler is designed to catch standard python logging messages, and send them to
    loguru (with appropriate additional metadata).

    For example, a component based on FastAPI (and thus Uvicorn) can use the
    component_specific_loggers_config argument to make it so that the python loggers "fastapi" and
    "uvicorn", "uvicorn.error" and "uvicorn.access" are intercepted at level DEBUG, and logger for
    "sqlalchemy" is intercepted at level WARNING.

    Note: there is no way, as of today, to apply filters or formatters for interception.

    **Loguru outputs in details**

    Loguru receives everything that is intercepted. Remains to define loguru's outputs.

    By default, two "sinks" are defined : loki and stderr.

    All that is intercepted is sent to Loki as-is. The filtering can then be done in the
    Loki/Graphana dashboard, if necessary.

    By default (if loguru_outputs_handlers is None), a second sink to stderr is defined, with
    specific level (main_logger_level), format, and filters. This sink prints to stderr, only
    messages above level main_logger_level, with a format that gives a lot of details, and
    potentially some filters, if specified in the component_specific_loggers_config parameter.
    Indeed, this parameter can contain, for a specific python standard logger, a "display_level"
    (i.e. a level specific for this logger), and a "display_filter" (a lambda function that takes the log
    record and returns a boolean). The difference between the "intercept_level" and the
    "display_level" is that the former will affect what is sent to Loki *and* to the stderr sink,
    and the disaply_level will only affect what is sent to the stderr sink.

    Alternatively, the defaut stderr sink can be completely overwrittent, by providing a non-None
    loguru_outputs_handlers argument. In this case, the "display_filter" and "display_level" of the
    component_specific_loggers_config argument will be ignored.


    **Structure of the component_specific_loggers_config argument**

    This parameter is used to tweak interception of python standard loggers, and (if
    loguru_outputs_handlers is None), the level and display filters (applied to the default stderr
    loguru sink) for those intercepted log records.

    Here is an example :

    ```
    component_specific_loggers_config = {
       "fastapi": {
        "intercept_level": logging.getLevelName("INFO"),
        "display_level": logging.getLevelName("ERROR")
       },
       "uvicorn.access": {
        "intercept_level": logging.getLevelName("DEBUG"),
        "display_level": logging.getLevelName("INFO")
        "display_filter": lambda record: '"GET /metrics HTTP/1.1" 200' not in record["message"]
       }
    }
    ```

    What this will do is:
    * Completely erase the current config of the fastapi and uvicorn.access standard python loggers
    * Set a new configuration for them:
        * fastapi will have level INFO and one handler (InterceptHandler) also at level INFO, and
          propagate will be False (so that it is not again intercepted and printed by the root logger)
        * uvicorn.access (which, in FastAPI apps, prints the GETs, POSTs etc.): will have a very
          similar configuration, except is level will be DEBUG
    * If any other standard python logger emits messages, it will be caught by the root logger. But
      at a level we do not know.
        * Note: if a particular library (say "annoyinglabrary") is too verbose and you want to avoid
          its prints, add something like `component_specific_loggers_config["annoyinglibrary"] =
          {"intercept_level": logging.getLevelName("ERROR")}`
    * If a Loki URL is configured, all intercepted messages go to Loki
    * If loguru_outputs_handlers is None, the stderr sink will be configured with a filter which will:
        * Discard all intercepted messages from fastapi that are below ERROR: they will not be printed
          to stderr
        * Discard all intercepted messages from uvicorn.access that are below INFO, *and* discard
          log records which message contains '"GET /metrics HTTP/1.1" 200'



    **Parameters:**

    :param labels: Labels of the component for the Loki instance (e.g. "it_simulation")
    :param loguru_outputs_handlers: Optional. If None, a default loguru handler is automatically
        created, that prints to stderr (see above). If not None, "display_level" and
        "display_filter" of component_specific_loggers_config are iggnored, and the list is passed
        as the list of handlers to loguru without changing them (no additional/automatic formatting
        or filtering). But in any cases, if a Loki URL is configured for the component, a handler
        is added to send a copy of all logged messages to Loki (that handler always has level
        NOTSET).
    :param main_logger_level: Optional, used only if loguru_outputs_handlers is None. It determines
        the default loguru handler automatically created, and the level of messages printed to to
        the default stderr loguru sink.
    :param main_logger_print_files_and_lines: Optional, used only if loguru_outputs_handlers is
        None. It tweaks the formatter of the default loguru handler automatically created, to print
        python modules and lines of messages are logged.
    :param component_specific_loggers_config: Optional. Can be used to specify levels for (python
        standard) loggers, and (when loguru_outputs_handlers is None) display levels and display
        filters to apply to the stderr loguru defaut sink (if loguru_outputs_handlers is None). See
        above.

    """

    _configure_interception(component_specific_loggers_config)

    _configure_loguru_outputs(
        loki_labels,
        force_no_loki,
        loguru_outputs_handlers,
        main_logger_level,
        main_logger_print_files_and_lines,
        component_specific_loggers_config,
        **kwargs,
    )


def _configure_interception(
    component_specific_loggers_config: Optional[Dict[str, Dict[str, Any]]]
) -> None:
    ##################################
    ## INPUTS/INTERCEPTION SECTION
    ## Setup interception of python std logs
    ##################################

    # The chosen strategy for interception is to :
    # - Replace a list of logger defined by the user (it depends on the component), with loggers of our own level and witrh 1 handler (our InterceptHandler)
    # - Replace the logging.lastResort handler (called when a message is propagated all the way
    #   _above_ the root logger, and has never been printed) with our InterceptHandler

    python_logging_config = {
        "version": 1,
        # Leave untouched any other loggers that may be configured. It is up to the user of the
        # configure() function to provide its whitelist of loggers to override
        "disable_existing_loggers": False,
        # Incremental = False means that we *replace* the loggers mentionned in this config
        "incremental": False,
        # There is no formatter, because all formatters (of pre-existing, new, of really any logger)
        # will effectively be ignored. We intercept the message and put them in loguru. It is
        # loguru's formatter(s) that count
        "formatters": {},
        # Same for filters. We do not filter at intercept, but at disaply
        "filters": {},
        # The only handler is goign to be our InterceptHandler. Do not manage the level here, but in the loggers itself
        "handlers": {
            "intercept_handler": {
                "class": "mantis_logger.handlers.InterceptHandler",
                "level": logging.NOTSET,
            },
        },
        # The list of logger will be defined after
        "loggers": {},
        # Root logger : empty handlers, and let the lastResort handler catch log messages that were not already processed by other handlers
        "root": {"level": logging.NOTSET, "handlers": []},
    }

    if component_specific_loggers_config is not None:
        # Root logger specific config
        root_level = component_specific_loggers_config.get("root", {}).get(
            "intercept_level", None
        )
        if root_level is not None:
            python_logging_config["root"]["level"] = root_level

        # Add or overwrite loggers asked by the user
        for logger_name, logger_config in component_specific_loggers_config.items():
            if logger_name == "root":
                continue
            python_logging_config["loggers"][logger_name] = {
                "handlers": ["intercept_handler"],
                "propagate": False,
            }
            if "intercept_level" in logger_config:
                python_logging_config["loggers"][logger_name]["level"] = logger_config[
                    "intercept_level"
                ]

    # Configure in bulk the loggers. This will erase and recreate (or just create) all loggers we specified
    logging.config.dictConfig(python_logging_config)

    # Replace the last resort handler as well(this lastResort handler is called only if no handler
    # have printed a message, after propagation of the message all the way even _above_ the root
    # logger)
    if not isinstance(logging.lastResort, InterceptHandler):  # Do not replace twice
        logging.lastResort = InterceptHandler(level=logging.NOTSET)


def _configure_loguru_outputs(
    loki_labels: Optional[Dict[str, str]],
    force_no_loki: bool,
    loguru_outputs_handlers: Optional[List[Dict[str, Any]]] = None,
    main_logger_level: Optional[str] = None,
    main_logger_print_files_and_lines: bool = True,
    component_specific_loggers_config: Optional[Dict[str, Dict[str, Any]]] = None,
    **kwargs,
) -> None:

    ##################################
    ## OUTPUTS SECTION
    ## Setup "outputs" towards loguru
    ##################################

    if loguru_outputs_handlers is None:
        # See if any loguru filters were given (that need to be applied to the "main handler", but not to the loki handler)

        main_logger_subfilters: List[Callable[[Dict[str, Any]], bool]] = []
        if component_specific_loggers_config is not None:
            for (
                logger_name,
                logger_specific_config,
            ) in component_specific_loggers_config.items():
                if (
                    "display_filter" in logger_specific_config
                    or "display_level" in logger_specific_config
                ):
                    main_logger_subfilters.append(
                        _make_one_subfilter(
                            logger_name,
                            logger_specific_config.get("display_filter", None),
                            logger_specific_config.get("display_level", None),
                        )
                    )

        # Setup the loguru handler to print to stdout (or stderr, rather)
        if main_logger_level is None:
            main_logger_level = loguru._defaults.LOGURU_LEVEL

        loguru_outputs_handlers = [
            {
                "sink": sys.stderr,
                "level": main_logger_level,
                "backtrace": False,
                "diagnose": True,
                "format": _make_main_logger_format(main_logger_print_files_and_lines),
                "filter": _make_main_logger_filter(main_logger_subfilters),
            }
        ]

    # Setup handlers for Loki (loguru and stdlib loggers)
    # No filter, an level NOTSET to capture everything
    if mantis_logger_config.loki_url and not force_no_loki:
        loguru_outputs_handlers.append(
            {
                "sink": CentralizedLoggerHandler(labels=loki_labels),
                "level": logging.NOTSET,  # catch all log levels
                "serialize": True,
            }
        )

    logger.configure(handlers=loguru_outputs_handlers, **kwargs)
    logger.disable(__name__)
    if mantis_logger_config.loki_url:
        # prevent endless loop between loki handler and urllib3 logger
        logger.disable("urllib3.connectionpool")


def _make_one_subfilter(
    logger_name: str,
    display_filter: Optional[Callable[[Dict[str, Any]], bool]],
    display_level: Optional[int],
) -> Callable[[Dict[str, Any]], bool]:
    assert display_filter is not None or display_level is not None

    def subfilt_level(record: Dict[str, Any]) -> bool:
        return record["level"].no >= display_level

    def subfilt_both(record: Dict[str, Any]) -> bool:
        return display_filter(record) and record["level"].no >= display_level

    if display_filter is not None and display_level is None:
        effective_subfilt = display_filter
    elif display_filter is None and display_level is not None:
        effective_subfilt = subfilt_level
    else:
        effective_subfilt = subfilt_both

    def subfilt(record: Dict[str, Any]) -> bool:
        if (
            "extra" in record
            and "name" in record["extra"]
            and record["extra"]["name"] == logger_name
        ):
            return effective_subfilt(record)
        else:
            return True

    return subfilt


def _make_main_logger_filter(
    subfilters: List[Callable[[Dict[str, Any]], bool]]
) -> Callable[[Dict[str, Any]], bool]:
    def filt(record: Dict[str, Any]) -> bool:
        return all(filt(record) for filt in subfilters)

    return filt


def _make_main_logger_format(
    print_files_and_lines: bool,
) -> Callable[[Dict[str, Any]], str]:
    if print_files_and_lines:
        _format = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{extra[name]: <15}</level>  | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    else:
        _format = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{extra[name]: <15}</level>  | <level>{level: <8}</level> | <level>{message}</level>"

    _format += "\n{exception}"

    def format(record: Dict[str, Any]) -> str:
        if "name" not in record["extra"]:
            record["extra"]["name"] = ""
        return _format

    return format
