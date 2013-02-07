#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# guifiAPI.py - Guifi.net API handler
# Copyright (C) 2012 Pablo Castellano <pablo@anche.no>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


ANSWER_GOOD = 200
ANSWER_GOOD_STR = 'Request completed successfully'
ANSWER_BAD = 201
ANSWER_BAD_STR = 'Request could not be completed, errors found'

CODE_ERROR_BAD_FORMATTED = 400
CODE_ERROR_BAD_FORMATTED_STR = 'Request is not well-formatted: input command is empty or invalid'
CODE_ERROR_INVALID_COMMAND = 401
CODE_ERROR_INVALID_COMMAND_STR = 'Request is not valid: input command is not implemented'
CODE_ERROR_MISSING_FIELDS = 402
CODE_ERROR_MISSING_FIELDS_STR = 'Request is not valid: some mandatory fields are missing'
CODE_ERROR_MISSING_VALUES = 403
CODE_ERROR_MISSING_VALUES_STR = 'Request is not valid: some input data is incorrect'
CODE_ERROR_NOT_ALLOWED = 404
CODE_ERROR_NOT_ALLOWED_STR = 'Request is not valid: operation is not allowed'
CODE_ERROR_NOT_FOUND = 500
CODE_ERROR_NOT_FOUND_STR = 'Request could not be completed. The object was not found'
CODE_ERROR_FORBIDDEN = 501
CODE_ERROR_FORBIDDEN_STR = 'You don\'t have the required permissions'
CODE_ERROR_INVALID_TOKEN = 502
CODE_ERROR_INVALID_TOKEN_STR = 'The given Auth token is invalid'
