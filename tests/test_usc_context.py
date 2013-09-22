#!/usr/bin/env python

import os
import sys
import unittest
os.chdir(os.path.abspath(os.path.dirname(__file__)))
os.chdir('..')
sys.path.append('.')
import logging
import unsolclic
import tempfile

unsolclic.logger.setLevel(logging.NOTSET)

SAVE_ON_ERROR = True
ROOT_PATH = os.path.abspath(os.path.dirname('.'))
DATA_PATH = os.path.join(os.path.join(ROOT_PATH, 'tests'), 'data')

DATA = {
    24366: {
        'ack': '',
        'dev': {'nick': 'BCNrossello208-OMNITIK'},
        'ext_antenna': '',
        'ipv4_ip': '',
        'ipv4_netmask': '',
        'mcastrate': '',
        'net_mode': '',
        'node_nick': 'BCNrossello208',
        'radio1txpower': '',
        'radio_rx': '2',
        'radio_tx': '2',
        'rate_max': '',
        'wangateway': '',
        'wireless1ssid': '',
        'zone_primary_dns': '10.228.203.104',
        'zone_secondary_dns': '10.139.6.130'
    },
    26505: {
        'ack': '25',
        'dev': {'nick': 'BCNrossello208-NSBR5'},
        'ext_antenna': 'disabled',
        'ipv4_ip': '',
        'ipv4_netmask': '',
        'mcastrate': '54',
        'net_mode': 'a',
        'node_nick': 'BCNrossello208',
        'radio1txpower': '6',
        'radio_rx': '2',
        'radio_tx': '2',
        'rate_max': '54M',
        'wangateway': '',
        'wireless1ssid': '',
        'zone_primary_dns': '10.228.203.104',
        'zone_secondary_dns': '10.139.6.130'
    },
    26325: {
        'address': '',
        'antenna_mode': 'ant-a',
        'band': '5ghz-a',
        'broadcast': '',
        'channel_width': '20mhz',
        'dev': {'id': '26325', 'nick': 'BCNrossello208-RB1100', 'node_nick': 'BCNrossello208',
                'logserver': '',  # {{ dev.radios[0].ipv4}}
                'radios': [
                    [0, {'id': '', 'radiodev_counter': 0, 'ssid': 'BCNrossello208Main',
                         'mode': 'ap-bridge', 'antenna_gain': '5', 'channel': '5260',
                         'interfaces': [[0, {'interface_type': 'wLan/Lan'}]]}],
                    [1, {'id': '', 'radiodev_counter': 1, 'ssid': 'BCNrossello208-jverne5',
                         'mode': 'ap-bridge', 'antenna_gain': '14', 'channel': '5700',
                         'interfaces': [[0, {'interface_type': 'wds/p2p'}]]}],
                    [2, {'id': '', 'radiodev_counter': 2, 'ssid': 'BCNrossello208-jardibotanic',
                         'mode': 'ap-bridge', 'antenna_gain': '14', 'channel': '',
                         'interfaces': [[0, {'interface_type': 'wds/p2p'}]]}],
                    [3, {'id': '', 'radiodev_counter': 3, 'ssid': 'BCNxsf-coopCrmlWDSAP5G',
                         'mode': 'ap-bridge', 'antenna_gain': '14', 'channel': '5680',
                         'interfaces': [[0, {'interface_type': 'wds/p2p'}]]}],
                    [4, {'id': '', 'radiodev_counter': 4, 'ssid': 'BCNrossello208F5AP0',
                         'mode': 'ap-bridge', 'antenna_gain': '8', 'channel': '5260',
                         'interfaces': [[0, {'interface_type': 'wLan'}]]}]]
                },
        'disabled': '',
        'firewall': '',
        'firmware_name': 'RouterOSv5.x',
        'host_name': '',
        'hotspot_ssid': '',
        'id': '',
        'iname': '',
        'interface_name': '',
        'ip': '',
        'ipv4': {'ipv4': '', 'maskbits': '', 'netid': '', 'broadcast': '',
                 'ospf_name': ''},
        'link': {'interface':
                 {'ipv4':
                  {'host_name': ''}
                  }
                 },  # {{ link.interface.ipv4.host_name }}
        'link_mac': '',
        'maskbits': '',
        'netid': '',
        'netmask': '',
        'netwok': '',  # typo?
        'network': '',
        'ospf_name': '',
        'ospf_routerid': '10.228.192.193',
        'poolend': '',
        'poolstart': '',
        'primary_dns': '',
        'radio_id': '',
        'rmac': '',
        'secondary_dns': '',
        'snmp_contact': 'guifi@guifi.net',
        'zone_id': '2436',
        'zone_primary_dns': '10.228.203.104',
        'zone_primary_ntp': '10.228.203.104',
        'zone_secondary_dns': '10.139.6.130',
        'zone_secondary_ntp': '10.138.27.194',
    }
}


class UnsolclicTestCase(unittest.TestCase):
    # Device 26328 (BCNrossello208-OMNITIK) from node 24366 (BCNrossello208)
    # http://guifi.net/es/guifi/device/26328
    # http://guifi.net/files/nanostation/BCNrossello208-OMNITIK.cfg
    device_id = 24366
    template_file = 'AirOsv30'
    result_file = 'BCNrossello208-OMNITIK.cfg'

    def setUp(self):
        self.usc = unsolclic.UnSolClic()

    def test_fromContext(self):
        #print self.result_file
        context = DATA[self.device_id]
        filepath = os.path.join(DATA_PATH, self.result_file)
        r1 = self.usc.generate_from_context(self.template_file, context)
        with open(filepath) as fp:
            r2 = fp.read()

        r1 = r1.encode('utf-8')
        #r2 = r2.encode('utf-8')

        if r1[0] == '\n':
            r1 = r1[1:]
        if r2[-1] == '\n':
            r2 = r2[:-1]
        try:
            self.assertEqual(r1, r2)
        except AssertionError:
            if SAVE_ON_ERROR:
                uid = "-%s_%s_" % (self.template_file, str(self.device_id))
                tmpfile1 = tempfile.mktemp(uid + '_1')
                tmpfile2 = tempfile.mktemp(uid + '_2')
                with open(tmpfile1, 'w') as fp:
                    fp.write(r1)
                with open(tmpfile2, 'w') as fp:
                    fp.write(r2)

                print 'Assertion error: generated unsolclic differs from expected result'
                print 'Both results were saved so that you can manually check them:'
                print 'diff -u %s %s' % (tmpfile1, tmpfile2)
            raise


class AirOsv30SortedContextTestCase(UnsolclicTestCase):
    device_id = 24366
    template_file = 'AirOsv30_sorted'
    result_file = 'BCNrossello208-OMNITIK_sorted.cfg'


# NOTE: website says AirOSv3.6+
class AirOsv36ContextTestCase(UnsolclicTestCase):
    # Device 26505 (BCNrossello208-NSBR5) from node 24366 (BCNrossello208)
    # http://guifi.net/es/guifi/device/26505/view/unsolclic
    # http://guifi.net/files/nanostation/BCNrossello208-NSBR5.cfg
    device_id = 26505
    template_file = 'AirOsv30'
    result_file = 'BCNrossello208-NSBR5.cfg'


# RouterOSv5.x
class RouterOSv50ContextTestCase(UnsolclicTestCase):
    # Device 26325 (BCNrossello208-RB1100) from node 24366 (BCNrossello208)
    # http://guifi.net/ca/guifi/device/26325/view/unsolclic
    device_id = 26325
    template_file = 'RouterOSv5.x.twig'
    result_file = '26325_routeros5x'


if __name__ == '__main__':
    unittest.main()
