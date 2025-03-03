# Copyright (c) 2019 Cobus Nel
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

"""
Convenience functions and classes dealing with logging
"""
import os
import logging
import sys
from logging.handlers import QueueHandler, QueueListener

from .. import DEFAULT_LOG_MESSAGE


DEFAULT_LOG_LEVEL = logging.INFO


def init_logger(message=None, name=None, level=DEFAULT_LOG_LEVEL, handler=None):
    """
    generic logger initialization function
    """
    logger = logging.getLogger(name)
    _message = message or DEFAULT_LOG_MESSAGE
    formatter = logging.Formatter(_message)
    handler = handler or logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(level)
    return logger


def init_null_logger(message=None, name=None):
    """
    logger that does nothing
    """
    logger = logging.getLogger(name)
    logger.addHandler(logging.NullHandler())
    return logger


def init_file_logger(filename, message=None, name=None, level=DEFAULT_LOG_LEVEL):
    """
    Return simple file logger
    """
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    handler = logging.FileHandler(filename)
    return init_logger(message, name, level, handler)


def init_rotating_file_logger(filename, message=None, name=None,
                              level=DEFAULT_LOG_LEVEL,
                              max_bytes=20 * 1024 * 1024,
                              backup_count=10):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    handler = logging.handlers.RotatingFileHandler(
        filename, maxBytes=max_bytes, backupCount=backup_count
    )
    return init_logger(message, name, level, handler)


def init_stream_logger(stream, message=None, name=None, level=DEFAULT_LOG_LEVEL):
    """
    Return stream logger
    """
    handler = logging.StreamHandler(stream)
    return init_logger(message, name, level, handler)


def init_stderr_logger(message=None, name=None, level=DEFAULT_LOG_LEVEL):
    """
    Return stream logger to stderr
    """
    return init_stream_logger(sys.stderr, message=None, name=None, level=level)


def init_stdout_logger(message=None, name=None, level=DEFAULT_LOG_LEVEL):
    """
    Return stream logger to stderr
    """
    return init_stream_logger(sys.stdout, message=None, name=None, level=level)


def init_queue_logger(queue, name, level=DEFAULT_LOG_LEVEL):
    """
    initialize queue logging for multi-processing
    """
    logger = logging.getLogger(name)
    handler = QueueHandler(queue)
    handler.setLevel(level)
    logger.addHandler(handler)
    return logger


def init_queue_listener(queue):
    """
    init a queue listener

    rememeber to start and stop
    """
    # _message = message or DEFAULT_LOG_MESSAGE
    # _handler = handler or logging.StreamHandler(sys.stderr)
    # _formatter = logging.Formatter(_message)
    # _handler.setFormatter(_formatter)
    # _handler.setLevel(level)
    listener = QueueListener(queue, *logging.getLogger(__name__).handlers)
    return listener
