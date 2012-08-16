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

from utils import I18N_APP_NAME, I18N_APP_DIR

import gettext
gettext.bindtextdomain(I18N_APP_NAME, I18N_APP_DIR)
gettext.textdomain(I18N_APP_NAME)
_ = gettext.gettext


try:
	from gi.repository import GnomeKeyring
	USE_GNOME_KEYRING = GnomeKeyring.is_available()
	KEYRING_NAME = 'login' #default keyring that gets unlocked normally when the user starts the session
	GUIFINETLOGINKEYNAME = 'guifinetlogin'
	print _('Use GNOME Keyring:'), USE_GNOME_KEYRING
	GnomeKeyring.unlock_sync(KEYRING_NAME, None)
except ImportError:
	print _('GNOME Keyring dependency not available')
	print _('Using plain text configuration files instead')
	USE_GNOME_KEYRING = False

class GuifinetStudioConfig:
	CONFIG_DIR = os.path.expanduser('~/.config/guifinetstudio')
	CACHE_DIR = os.path.expanduser('~/.cache/guifinetstudio')
	CONFIG_FILENAME = os.path.join(CONFIG_DIR, 'config')
	
	def __init__(self):
		#create config folder and default file if they don't exist
		self.initConfig()
			
		self.config = ConfigParser.SafeConfigParser()
		self.reload()


	def initConfig(self):
		if not os.path.exists(self.CONFIG_DIR):
			print _('No configuration found. Creating a default one in'), self.CONFIG_DIR
			os.mkdir(self.CONFIG_DIR)
			self.createDefaultConfig()
		elif not os.path.exists(self.CONFIG_FILENAME):
			self.createDefaultConfig()
			
		if not os.path.exists(self.CACHE_DIR):
			print _('No cache folder found. Creating'), self.CACHE_DIR
			os.mkdir(self.CACHE_DIR)
			os.mkdir(os.path.join(self.CACHE_DIR, 'zones'))
			os.mkdir(os.path.join(self.CACHE_DIR, 'nodes'))
			os.mkdir(os.path.join(self.CACHE_DIR, 'detail'))
		
	
	def reload(self):
		try:
			res = self.config.read(self.CONFIG_FILENAME)
			if res == []:
				raise Exception
		except Exception:
			print _('Error reading file:'), self.CONFIG_FILENAME
			raise
			
			
	def save(self):
		with open(self.CONFIG_FILENAME, 'w') as fp:
			self.config.write(fp)


	def createDefaultConfig(self):
		defaultconfig = ConfigParser.SafeConfigParser()
		defaultconfig.add_section('api')
		defaultconfig.set('api', 'username', '')
		
		if USE_GNOME_KEYRING:
			self.gkr_store(GUIFINETLOGINKEYNAME, ':')
			
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
		if USE_GNOME_KEYRING:
			username = self.gkr_get(GUIFINETLOGINKEYNAME)
			if username is None:
				print _('Error reading username in GNOME Keyring :-(')
			else:
				return username.split(':')[0]
		else:
			return self.config.get('api', 'username')

	
	def setUsername(self, username):
		if USE_GNOME_KEYRING:
			self.gkr_store(GUIFINETLOGINKEYNAME, '%s:%s' %(username, self.getPassword()))
		else:
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
		if USE_GNOME_KEYRING:
			password = self.gkr_get(GUIFINETLOGINKEYNAME)
			if password is None:
				print _('Error reading password in GNOME Keyring :-(')
			else:
				return password.split(':')[1]
		else:
			return self.config.get('api', 'password')

		
	def setPassword(self, password):
		if USE_GNOME_KEYRING:
			self.gkr_store(GUIFINETLOGINKEYNAME, '%s:%s' %(self.getUsername(), password))
		else:
			self.config.set('api', 'password', password)
		

	def getHost(self):
		return self.config.get('api', 'host')
		

	def setHost(self, host):
		self.config.set('api', 'host', host)
		

	def getAuthToken(self):
		return self.config.get('api', 'token')
		
		
	def setAuthToken(self, token):
		#print '<<<setAuthToken>>>', token
		self.config.set('api', 'token', token)
		
		
	def getAuthTokenDate(self):
		tokendate = self.config.get('api', 'token_date')
		
		if tokendate == '':
			return None
		else:
			return datetime.strptime(tokendate, '%Y-%m-%d %H:%M:%S.%f')
		
		
	def setAuthTokenDate(self, tokendate=None):
		#print '<<<setAuthTokenDate>>>', tokendate
		if not tokendate:
			tokendate = str(datetime.now())
			
		self.config.set('api', 'token_date', tokendate)
		
		
	def pathForCNMLCachedFile(self, zid, ctype='nodes'):
		if ctype not in ['zones', 'nodes', 'detail']:
			raise ValueError
			
		return '%s/%s/%d.cnml' %(self.CACHE_DIR, ctype, zid)


	def gkr_store(self, id, secret):
		GnomeKeyring.create_sync(KEYRING_NAME, None)
		attrs = GnomeKeyring.Attribute.list_new()
		GnomeKeyring.Attribute.list_append_string(attrs, 'id', id)
		GnomeKeyring.item_create_sync(KEYRING_NAME, GnomeKeyring.ItemType.GENERIC_SECRET, id, attrs, secret, True)


	def gkr_get(self, id):
		attrs = GnomeKeyring.Attribute.list_new()
		GnomeKeyring.Attribute.list_append_string(attrs, 'id', id)
		result, value = GnomeKeyring.find_items_sync(GnomeKeyring.ItemType.GENERIC_SECRET, attrs)
		if result == GnomeKeyring.Result.OK:
			return value[0].secret
		elif result == GnomeKeyring.Result.NO_MATCH:
			# Key doesn't exist, create again
			print _("Key doesn't exist in GNOME Keyring. Creating again...")
			self.gkr_store(GUIFINETLOGINKEYNAME, ':')
			return ''
		else:	
			return None
