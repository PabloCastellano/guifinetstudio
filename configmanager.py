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
from datetime import datetime

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
		defaultconfig.set('api', 'host', 'test.guifi.net')
		defaultconfig.set('api', 'token', '')
		defaultconfig.set('api', 'token_date', '')
		defaultconfig.add_section('general')
		defaultconfig.set('general', 'zone', '')
		defaultconfig.set('general', 'zone_type', '')
		defaultconfig.set('general', 'contact', '')
		
		with open(self.CONFIG_FILENAME, 'wb') as configfile:
			defaultconfig.write(configfile)

	def getContact(self):
		return self.config.get('general', 'contact')

	def setContact(self, contact):
		self.config.set('general', 'contact', contact)
	
	def getUsername(self):
		return self.config.get('api', 'username')
	
	def setUsername(self, username):
		self.config.set('api', 'username', username)
			
	def getDefaultZone(self):
		zone = self.config.get('general', 'zone')
		if zone == '':
			return None
		else:
			return int(zone)
		
	def setDefaultZone(self, zid):
		self.config.set('general', 'zone', str(zid))
	
	def getDefaultZoneType(self):
		return self.config.get('general', 'zone_type')
		
	def setDefaultZoneType(self, ztype):
		if ztype not in ['zones', 'nodes', 'detail']:
			raise ValueError
		self.config.set('general', 'zone_type', ztype)
	
	def getPassword(self):
		return self.config.get('api', 'password')
		
	def setPassword(self, password):
		self.config.set('api', 'password', password)
		
	def getHost(self):
		return self.config.get('api', 'host')
		
	def setHost(self, host):
		self.config.set('api', 'host', host)
		
	def getAuthToken(self):
		return self.config.get('api', 'token')
		
	def setAuthToken(self, token):
		print '<<<setAuthToken>>>', token
		self.config.set('api', 'token', token)
		
	def getAuthTokenDate(self):
		tokendate = self.config.get('api', 'token_date')
		
		if tokendate == '':
			return None
		else:
			return datetime.strptime(tokendate, '%Y-%m-%d %H:%M:%S.%f')
		
	def setAuthTokenDate(self, tokendate=None):
		print '<<<setAuthTokenDate>>>', tokendate
		if not tokendate:
			tokendate = str(datetime.now())
			
		self.config.set('api', 'token_date', tokendate)
		
	def pathForCNMLCachedFile(self, zid, ctype='nodes'):
		if ctype not in ['zones', 'nodes', 'detail']:
			raise ValueError
			
		return '%s/%s/%d.cnml' %(self.CACHE_DIR, ctype, zid)
