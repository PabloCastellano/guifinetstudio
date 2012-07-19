#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# configmanager.py - Explore your free network offline! Config Manager
# Copyright (C) 2011-2012 Pablo Castellano <pablo@anche.no>
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

import os
import ConfigParser

CONFIG_DIR = '~/.config/guifinetstudio'
full_config_dir = os.path.expanduser(CONFIG_DIR)
config_filename = os.path.join(full_config_dir, 'config')

#TODO: Use different backends: config file, gnome-keyring...

class GuifinetStudioConfig:
	def __init__(self):
		if not os.path.exists(full_config_dir):
			print 'No configuration found. Creating a default one in', full_config_dir
			os.mkdir(full_config_dir)
			self.createDefaultConfig()
		elif not os.path.exists(config_filename):
			self.createDefaultConfig()
			
		self.config = ConfigParser.SafeConfigParser()
		self.config.read(config_filename)

	def createDefaultConfig(self):
		defaultconfig = ConfigParser.SafeConfigParser()
		defaultconfig.add_section('api')
		defaultconfig.set('api', 'username', '')
		defaultconfig.set('api', 'password', '')
		
		with open(config_filename, 'wb') as configfile:
			defaultconfig.write(configfile)

	def getUsername(self):
		return self.config.get('api', 'username')
		
	def getPassword(self):
		return self.config.get('api', 'password')
