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


from urllib2 import Request, urlopen, HTTPError, URLError
# Warning: HTTPS requests do not do any verification of the server’s certificate.
# Currently urllib2 does not support fetching of https locations through a proxy. This can be a problem.
# http://www.voidspace.org.uk/python/articles/urllib2.shtml

from error import GuifiApiError
from constants import *

import urllib

import base64

import sys
import json

class GuifiAPI:
		
	def __init__(self, username=None, passwd=None, 
				host='test.guifi.net', secure=False,
				retry_count=0, retry_delay=0, retry_errors=None):
					
		self.setHost(host)
		self.secure = secure
		self.username = username
		self.passwd = passwd
		self.retry_count = retry_count
		self.retry_delay = retry_delay
		self.retry_errors = retry_errors
		self.authToken = None
		
		self.base_url = 'https://' if self.secure else 'http://'
		self.base_url += self.host
		
		self.base_api_url = self.base_url + '/api?'

		user_agent = 'pyGuifiAPI/1.0'
 		self.headers = {'User-Agent':user_agent}
		
	
	def getHost(self):
		return self.host
		
	def setUsername(self, username):
		if username != self.username:
			#invalidate auth token
			self.authToken = None
			self.username = username
	
	
	def setPassword(self, password):
		self.passwd = password
		
		
	def setHost(self, host):
		"""Checks for a valid host and set it as attribute"""
		if host.endswith('/'):
			host = host[:-1]
		
		self.host = host
	
	
	def sendRequest(self, data):
		""" Sends API request and returns json result"""
		url = self.base_api_url + data
		print '<<<sendRequest>>>', url, len(url)
		print 'Headers:', self.headers
		
		req = Request(url, headers=self.headers)
		try:
			response = urlopen(req)
			#j = json.load(response)
			r = response.read()
			j = json.loads(r)
			print r
		except URLError, e:
			#caza tambien HTTPError
			print e.reason
			raise
		except ValueError, e:
			print e.reason
			raise
	
		return self._parseResponse(j)
	
	
	def _parseResponse(self, jsondata):
		""" Parses json response.
		    Returns a tuple with the code and the result of the request (it can be an errorenous response)
		    Raises exception if any error code is unknown """
		print '<<<parseResponse>>>'
		codenum = jsondata.get('code')['code']
		codestr = jsondata.get('code')['str']
		
		print 'Got code %d: %s' %(codenum, codestr)
			
		if codenum == ANSWER_GOOD:
			responses = jsondata.get('responses')
			if isinstance(responses, list):
				if len(responses) == 1:
					responses = responses[0]
					print 'Just one response'
				else:
					print 'There are several responses'
			return (codenum, responses)
		elif codenum == ANSWER_BAD:
			errors = jsondata.get('errors')
			if len(errors) == 1:
				errors = errors[0]
				print 'Just one response (error)'
				print 'Error', errors['code'], ':', errors['str']
				print 'Extra information:', errors['extra']
			else:
				print 'There are several responses (errors)'
				for e in errors:
					print 'Error', e['code'], ':', e['str']
					print 'Extra information:', e['extra']
			return (codenum, errors)
		else:
			raise GuifiApiError('Unexpected return code: '+codenum)
	
		
	def auth(self):
		""" Authenticate user and get the Authorization Token """
		
		if self.username is None or self.passwd is None:
			raise GuifiApiError('You need to set username and password first')
			
		self.authToken = None
		if self.headers.has_key('Authorization'):
			del self.headers['Authorization']
		
		# XXX: There's some kind of bug when you submit the Authorization header to this command
		# Then, you get 502 error if command is the last parameters specified
		# http://test.guifi.net/api?username=user1&password=pass1&command=guifi.auth.login
		# {"command":"","code":{"code":201,"str":"Request could not be completed, errors found"},"errors":[{"code":502,"str":"The given Auth token is invalid"}]}
		# Note 1: the command is not specified in the response (!!)
		# Note 2: it works well in firefox
		# A workaround fix is also using the method parameter which is added to the end in the dict structure
		#data = urllib.urlencode({'command':'guifi.auth.login', 'username':self.username, 'password':self.passwd})
		data = urllib.urlencode({'command':'guifi.auth.login', 'username':self.username, 'password':self.passwd, 'method':'password'})
		
		try:
			(codenum, response) = self.sendRequest(data)
		
			print 'auth:', codenum
			print response
			
			if codenum == ANSWER_GOOD:
				self.authToken = response.get('authToken')
				self.headers['Authorization'] = 'GuifiLogin auth='+self.authToken
			else:
				# Expect just one error
				errorcode = response['code']
				if errorcode == CODE_ERROR_INVALID_TOKEN: # Nosense (:?)
					#{"errors":[{"code":403,"str":"Request is not valid: some input data is incorrect","extra":"Either the supplied username or password are not correct"}]}
					raise GuifiApiError('Error during authentication: '+str(errorcode)+ ': '+response['str'])
				else:
					raise GuifiApiError('Unexpected return code: '+errorcode)
		except URLError: # Not connected to the Internets
			raise
	
	
	def addNode(self, title, zone_id, lat, lon, nick=None, body=None,
					zone_desc=None, notification=None, elevation=None,
					stable='Yes', graph_server=None, status='Planned'):
		
		if not self.is_authenticated():
			raise GuifiApiError('You have to be authenticated to run this action')
		
		data = {'command':'guifi.node.add', 'title':title, 'zone_id':zone_id, 'lat':lat, 'lon':lon}
		
		if nick is not None:
			data['nick'] = nick
		if body	is not None:
			data['body'] = body
		if zone_desc is not None:
			data['zone_description'] = zone_desc
		if notification	is not None:
			data['notification'] = notification
		if elevation is not None:
			data['elevation'] = elevation
		if stable is not 'Yes':
			data['stable'] = stable
		if graph_server	is not None:
			data['graph_server'] = graph_server
		if status is not 'Planned':
			data['status'] = status
			
		params = urllib.urlencode(data)
		(codenum, response) = self.sendRequest(params)
		
		if codenum == ANSWER_GOOD:
			node_id = int(response.get('node_id'))
			print 'Node succesfully created', node_id
			print '%s/node/%d' %(self.base_url, node_id)
		else:
			# Everybody can create nodes
			raise GuifiApiError(response['str'], response['code'], response['extra'])
			
		return node_id
		
	def urlForNode(self, nid):
		return '%s/node/%d' %(self.base_url, nid)
	
	def updateNode(self, nid, title=None, nick=None, body=None,
					zone_id=None, zone_desc=None, notification=None,
					lat=None, lon=None, elevation=None, stable=None,
					graph_server=None, status=None):
		
		if not self.is_authenticated():
			raise GuifiApiError('You have to be authenticated to run this action')
		
		data = {'command':'guifi.node.update', 'node_id':nid}
		if title is not None:
			data['title'] = title
		
		params = urllib.urlencode(data)
		(codenum, response) = self.sendRequest(params)
		
		if codenum == ANSWER_GOOD:
			node_id = response['node']['node_id']
			print 'Node succesfully updated', node_id
			print '%s/node/%s' %(self.base_url, node_id)
		else:
			# [{"code":500,"str":"Request could not be completed. The object was not found","extra":"zone_id =  is not a guifi node"}]}
			raise GuifiApiError('Error updating node: '+str(response['str']))
			
		return node_id
		
		
	def removeNode(self, nid):
		if not self.is_authenticated():
			raise GuifiApiError('You have to be authenticated to run this action')
			
		data = {'command':'guifi.node.remove', 'node_id':nid}
		params = urllib.urlencode(data)
		(codenum, response) = self.sendRequest(params)

		if codenum == ANSWER_GOOD:
			print 'Node %s succesfully removed' %nid
		else:
			# [{"code":500,"str":"Request could not be completed. The object was not found","extra":"node_id = 49836"}]}
			raise GuifiApiError('Error removing node: '+str(response['str']))
		
	
	def addZone(self, title, master, minx, miny, maxx, maxy, nick=None,
				mode='infrastructure', body=None, timezone='+01 2 2',
				graph_server=None, proxy_server=None, dns_servers=None,
				ntp_servers=None, ospf_zone=None, homepage=None,
				notification=None):
				
		if not self.is_authenticated():
			raise GuifiApiError('You have to be authenticated to run this action')
			
		data = {'command':'guifi.zone.add', 'title':title, 'master':master,
				'minx':minx, 'miny':miny, 'maxx':maxx, 'maxy':maxy}
		params = urllib.urlencode(data)
		(codenum, response) = self.sendRequest(params)

		if codenum == ANSWER_GOOD:
			pass
		else:
			raise GuifiApiError('Error: '+str(response['str']))
			
	
	def updateZone(self, zid, title=None, nick=None, mode='infrastructure',
				body=None, timezone='+01 2 2',	graph_server=None, 
				proxy_server=None, dns_servers=None, ntp_servers=None,
				ospf_zone=None, homepage=None, notification=None,
				master=None, minx=None, miny=None, maxx=None, maxy=None):
				
		if not self.is_authenticated():
			raise GuifiApiError('You have to be authenticated to run this action')
			
		data = {'command':'guifi.zone.update', 'zone_id':zid}
		params = urllib.urlencode(data)
		(codenum, response) = self.sendRequest(params)

		if codenum == ANSWER_GOOD:
			pass
		else:
			raise GuifiApiError('Error: '+str(response['str']))
			
	
	def removeZone(self, zid):
				
		if not self.is_authenticated():
			raise GuifiApiError('You have to be authenticated to run this action')
			
		data = {'command':'guifi.zone.remove', 'zone_id':zid}
		params = urllib.urlencode(data)
		(codenum, response) = self.sendRequest(params)

		if codenum == ANSWER_GOOD:
			pass
		else:
			raise GuifiApiError('Error: '+str(response['str']))
			

	def addDevice(self, nid, rtype, mac, nick=None, notification=None,
					comment=None, status=None, graph_server=None):
				
		if not self.is_authenticated():
			raise GuifiApiError('You have to be authenticated to run this action')
			
		data = {'command':'guifi.device.add', 'node_id':nid, 'type':rtype, 'mac':mac}
		params = urllib.urlencode(data)
		(codenum, response) = self.sendRequest(params)

		if codenum == ANSWER_GOOD:
			pass
		else:
			raise GuifiApiError('Error: '+str(response['str']))
			

	def updateDevice(self, did, nid=None, nick=None, notification=None,
					mac=None, comment=None, status=None, graph_server=None):
				
		if not self.is_authenticated():
			raise GuifiApiError('You have to be authenticated to run this action')
			
		data = {'command':'guifi.device.update', 'device_id':did}
		params = urllib.urlencode(data)
		(codenum, response) = self.sendRequest(params)

		if codenum == ANSWER_GOOD:
			pass
		else:
			raise GuifiApiError('Error: '+str(response['str']))
			
	def removeDevice(self, did):
				
		if not self.is_authenticated():
			raise GuifiApiError('You have to be authenticated to run this action')
			
		data = {'command':'guifi.device.remove', 'device_id':did}
		params = urllib.urlencode(data)
		(codenum, response) = self.sendRequest(params)

		if codenum == ANSWER_GOOD:
			pass
		else:
			raise GuifiApiError('Error: '+str(response['str']))
		
		
	def addRadio(self, mode, did, mac, angle=None, gain=None,
					azimuth=None, amode=None):
				
		if not self.is_authenticated():
			raise GuifiApiError('You have to be authenticated to run this action')
			
		data = {'command':'guifi.radio.add', 'mode':mode, 'device_id':did, 'mac':mac}
		params = urllib.urlencode(data)
		(codenum, response) = self.sendRequest(params)

		if codenum == ANSWER_GOOD:
			pass
		else:
			raise GuifiApiError('Error: '+str(response['str']))
			

	def updateRadio(self, did, radiodev, angle=None, gain=None,
					azimuth=None, amode=None):
				
		if not self.is_authenticated():
			raise GuifiApiError('You have to be authenticated to run this action')
			
		data = {'command':'guifi.radio.update', 'device_id':did, 'radiodev_counter':radiodev}
		params = urllib.urlencode(data)
		(codenum, response) = self.sendRequest(params)

		if codenum == ANSWER_GOOD:
			pass
		else:
			raise GuifiApiError('Error: '+str(response['str']))
	
	
	def removeRadio(self, did, radiodev):
				
		if not self.is_authenticated():
			raise GuifiApiError('You have to be authenticated to run this action')
			
		data = {'command':'guifi.radio.remove', 'device_id':did, 'radiodev_counter':radiodev}
		params = urllib.urlencode(data)
		(codenum, response) = self.sendRequest(params)

		if codenum == ANSWER_GOOD:
			pass
		else:
			raise GuifiApiError('Error: '+str(response['str']))
			

	def addInterface(self, did, radiodev):
				
		if not self.is_authenticated():
			raise GuifiApiError('You have to be authenticated to run this action')
			
		data = {'command':'guifi.interface.add', 'device_id':did, 'radiodev_counter':radiodev}
		params = urllib.urlencode(data)
		(codenum, response) = self.sendRequest(params)

		if codenum == ANSWER_GOOD:
			pass
		else:
			raise GuifiApiError('Error: '+str(response['str']))
			
			
	def removeInterface(self, iid):
				
		if not self.is_authenticated():
			raise GuifiApiError('You have to be authenticated to run this action')
			
		data = {'command':'guifi.interface.remove', 'interface_id':iid}
		params = urllib.urlencode(data)
		(codenum, response) = self.sendRequest(params)

		if codenum == ANSWER_GOOD:
			pass
		else:
			raise GuifiApiError('Error: '+str(response['str']))
			

	def addLink(self, fromdid, fromradiodev, todid, toradiodev,
				ipv4=None, status='Working'):
		
		if not self.is_authenticated():
			raise GuifiApiError('You have to be authenticated to run this action')
			
		data = {'command':'guifi.interface.add', 'from_device_id':fromdid,
				'from_radiodev_counter':fromradiodev, 'to_device_id':todid,
				'to_radiodev_counter':toradiodev}
		params = urllib.urlencode(data)
		(codenum, response) = self.sendRequest(params)

		if codenum == ANSWER_GOOD:
			pass
		else:
			raise GuifiApiError('Error: '+str(response['str']))


	def updateLink(self, lid, ipv4=None, status=None):
				
		if not self.is_authenticated():
			raise GuifiApiError('You have to be authenticated to run this action')
			
		data = {'command':'guifi.interface.add', 'link_id':lid}
		params = urllib.urlencode(data)
		(codenum, response) = self.sendRequest(params)

		if codenum == ANSWER_GOOD:
			pass
		else:
			raise GuifiApiError('Error: '+str(response['str']))
	
	
	def removeLink(self, lid):
				
		if not self.is_authenticated():
			raise GuifiApiError('You have to be authenticated to run this action')
			
		data = {'command':'guifi.interface.remove', 'link_id':lid}
		params = urllib.urlencode(data)
		(codenum, response) = self.sendRequest(params)

		if codenum == ANSWER_GOOD:
			pass
		else:
			raise GuifiApiError('Error: '+str(response['str']))
	
	def getModels(self, type=None, fid=None, supported=None):
		data = {'command':'guifi.misc.model'}
		params = urllib.urlencode(data)
		(codenum, response) = self.sendRequest(params)

		if codenum == ANSWER_GOOD:
			pass
		else:
			raise GuifiApiError('Error: '+str(response['str']))
			
			
	def getManufacturers(self):
		data = {'command':'guifi.misc.manufacturer'}
		params = urllib.urlencode(data)
		(codenum, response) = self.sendRequest(params)

		if codenum == ANSWER_GOOD:
			pass
		else:
			raise GuifiApiError('Error: '+str(response['str']))
	
	
	def getFirmwares(self, model_id=None):
		data = {'command':'guifi.misc.firmware'}
		params = urllib.urlencode(data)
		(codenum, response) = self.sendRequest(params)

		if codenum == ANSWER_GOOD:
			pass
		else:
			raise GuifiApiError('Error: '+str(response['str']))
	
	
	def getProtocols(self):
		data = {'command':'guifi.misc.protocol'}
		params = urllib.urlencode(data)
		(codenum, response) = self.sendRequest(params)

		if codenum == ANSWER_GOOD:
			pass
		else:
			raise GuifiApiError('Error: '+str(response['str']))
	
		
	def getChannels(self, protocol):
		data = {'command':'guifi.misc.channel', 'protocol':protocol}
		params = urllib.urlencode(data)
		(codenum, response) = self.sendRequest(params)

		if codenum == ANSWER_GOOD:
			pass
		else:
			raise GuifiApiError('Error: '+str(response['str']))
			
		
	def is_authenticated(self):
		return self.authToken is not None
		
		
	def downloadCNML(self):
		pass

"""
guifi.zone.nearest
guifi.radio.nearest


guifi.misc.firmware
guifi.misc.protocol
guifi.misc.channel """