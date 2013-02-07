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


class GuifiApiError(Exception):
    def __init__(self, reason, code=0, extra=None):
        self.reason = reason
        self.code = int(code)
        self.extra = extra

    def __str__(self):
        return self.reason
