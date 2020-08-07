#   -*- coding: utf-8 -*-
#
#   This file is part of validator-cli
#
#   Copyright (C) 2019 SKALE Labs
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.

import logging
import logging.handlers as py_handlers
from logging import Formatter

from utils.helper import safe_mk_dirs
from utils.constants import (LOG_FORMAT, LOG_BACKUP_COUNT,
                             LOG_FILE_SIZE_BYTES, LOG_DATA_PATH,
                             LOG_FILEPATH, DEBUG_LOG_FILEPATH,)


def init_log_dir():
    safe_mk_dirs(LOG_DATA_PATH)


def init_logger():
    f_handler = get_file_handler(LOG_FILEPATH, logging.INFO)
    debug_f_handler = get_file_handler(DEBUG_LOG_FILEPATH, logging.DEBUG)
    logging.basicConfig(level=logging.DEBUG, handlers=[
        f_handler, debug_f_handler])


def get_file_handler(log_filepath, log_level):
    formatter = Formatter(LOG_FORMAT)
    f_handler = py_handlers.RotatingFileHandler(log_filepath, maxBytes=LOG_FILE_SIZE_BYTES,
                                                backupCount=LOG_BACKUP_COUNT)
    f_handler.setFormatter(formatter)
    f_handler.setLevel(log_level)

    return f_handler
