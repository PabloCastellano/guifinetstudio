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


class GuifinetStudioConfig:
	CONFIG_DIR = os.path.expanduser('~/.config/guifinetstudio')
	CACHE_DIR = os.path.expanduser('~/.cache/guifinetstudio')
	CONFIG_FILENAME = os.path.join(CONFIG_DIR, 'config')
	#TODO: Use different backends: config file, gnome-keyring...
	
	def __init__(self):
		#create config folder and default file if they don't exist
		if not os.path.exists(self.CONFIG_DIR):
			print 'No configuration found. Creating a default one in', self.CONFIG_DIR
			os.mkdir(self.CONFIG_DIR)
			self.createDefaultConfig()
		elif not os.path.exists(self.CONFIG_FILENAME):
			self.createDefaultConfig()
		
		if not os.path.exists(self.CACHE_DIR):
			print 'No cache folder found. Creating', self.CACHE_DIR
			os.mkdir(self.CACHE_DIR)
			os.mkdir(os.path.join(self.CACHE_DIR, 'zones'))
			os.mkdir(os.path.join(self.CACHE_DIR, 'nodes'))
			os.mkdir(os.path.join(self.CACHE_DIR, 'detail'))
			
		self.config = ConfigParser.SafeConfigParser()
		self.reload()

	def reload(self):
		try:
			res = self.config.read(self.CONFIG_FILENAME)
			if res == []:
				raise Exception
		except Exception:
			print 'Error reading file:', self.CONFIG_FILENAME
			raise
			
	def save(self):
		with open(self.CONFIG_FILENAME, 'w') as fp:
			self.config.write(fp)

	def createDefaultConfig(self):
		defaultconfig = ConfigParser.SafeConfigParser()
		defaultconfig.add_section('api')
		defaultconfig.set('api', 'username', '')
		defaultconfig.set('api', 'password', '')
		defaultconfig.add_section('default')
		defaultconfig.set('default', 'zone', '')
		defaultconfig.set('default', 'contact', '')
		
		with open(self.CONFIG_FILENAME, 'wb') as configfile:
			defaultconfig.write(configfile)

	def getContact(self):
		return self.config.get('default', 'contact')

	def setContact(self, contact):
		self.config.set('default', 'contact', contact)
	
	def getUsername(self):
		return self.config.get('api', 'username')
	
	def setUsername(self, username):
		self.config.set('api', 'username', username)
			
	def getDefaultZone(self):
		return int(self.config.get('default', 'zone'))
		
	def setDefaultZone(self, zid):
		self.config.set('default', 'zone', str(zid))
	
	def getPassword(self):
		return self.config.get('api', 'password')
		
	def setPassword(self, password):
		self.config.set('api', 'password', password)
		
	def pathForCNMLCachedFile(self, zid, ctype='nodes'):
		if ctype not in ['zones', 'nodes', 'detail']:
			raise ValueError
			
		return '%s/%s/%d.cnml' %(self.CACHE_DIR, ctype, zid)
