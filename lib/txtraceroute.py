#!/usr/bin/env python
# coding: utf-8
#
# Copyright (c) 2012 Alexandre Fiori
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import operator
import os
import socket
import struct
import time

try:
	from twisted.internet import defer
	from twisted.internet import reactor
except ImportError:
	raise


HOPS = []


class iphdr(object):
    """
    This represents an IP packet header.
    ICMP Protocol and source 0.0.0.0

    @assemble packages the packet
    @disassemble disassembles the packet
    """
    def __init__(self, dst=None):
        self.version = 4
        self.hlen = 5
        self.tos = 0
        self.length = 20
        self.id = os.getpid()
        self.frag = 0
        self.ttl = 255
        self.proto = socket.IPPROTO_ICMP
        self.cksum = 0
        self.src = "0.0.0.0"
        self.saddr = socket.inet_aton(self.src)
        self.dst = dst or "0.0.0.0"
        self.daddr = socket.inet_aton(self.dst)
        self.data = ""

    def assemble(self):
        header = struct.pack('BBHHHBB',
                             (self.version & 0x0f) << 4 | (self.hlen & 0x0f),
                             self.tos, self.length + len(self.data),
                             socket.htons(self.id), self.frag,
                             self.ttl, self.proto)
        self._raw = header + "\x00\x00" + self.saddr + self.daddr + self.data
        return self._raw

    @classmethod
    def disassemble(self, data):
        self._raw = data
        ip = iphdr()
        pkt = struct.unpack('!BBHHHBBH', data[:12])
        ip.version = (pkt[0] >> 4 & 0x0f)
        ip.hlen = (pkt[0] & 0x0f)
        ip.tos, ip.length, ip.id, ip.frag, ip.ttl, ip.proto, ip.cksum = pkt[1:]
        ip.saddr = data[12:16]
        ip.daddr = data[16:20]
        ip.src = socket.inet_ntoa(ip.saddr)
        ip.dst = socket.inet_ntoa(ip.daddr)
        return ip


class icmphdr(object):
    def __init__(self, data=""):
        self.type = 8
        self.code = 0
        self.cksum = 0
        self.id = os.getpid()
        self.sequence = 0
        self.data = data

    def assemble(self):
        part1 = struct.pack("BB", self.type, self.code)
        part2 = struct.pack("!HH", self.id, self.sequence)
        cksum = self.checksum(part1 + "\x00\x00" + part2 + self.data)
        cksum = struct.pack("!H", cksum)
        self._raw = part1 + cksum + part2 + self.data
        return self._raw

    @classmethod
    def checksum(self, data):
        if len(data) & 1:
            data += "\x00"
        cksum = reduce(operator.add,
                       struct.unpack('!%dH' % (len(data) >> 1), data))
        cksum = (cksum >> 16) + (cksum & 0xffff)
        cksum += (cksum >> 16)
        cksum = (cksum & 0xffff) ^ 0xffff
        return cksum

    @classmethod
    def disassemble(self, data):
        self._raw = data
        icmp = icmphdr()
        pkt = struct.unpack("!BBHHH", data)
        icmp.type, icmp.code, icmp.cksum, icmp.id, icmp.sequence = pkt
        return icmp


class Hop(object):
    def __init__(self, target, ttl):
        self.proto = "icmp"

        self.found = False
        self.tries = 0
        self.last_try = 0
        self.remote_ip = None
        self.remote_icmp = None
        self.remote_host = None
        self.location = ""

        self.ttl = ttl
        self.ip = iphdr(dst=target)
        self.ip.ttl = ttl
        self.ip.id += ttl

        self.icmp = icmphdr('\x00' * 20)
        self.icmp.id = self.ip.id
        self.ip.data = self.icmp.assemble()

        self._pkt = self.ip.assemble()

    @property
    def pkt(self):
        self.tries += 1
        self.last_try = time.time()
        return self._pkt

    def __repr__(self):
        if self.found:
            if self.remote_host:
                ip = self.remote_host
            else:
                ip = self.remote_ip.src
        else:
            ip = "??"

        return ip


# ICMP
class TracerouteProtocol(object):
    def __init__(self, target, **settings):
        self.target = target
        self.settings = settings
        self.rfd = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
        self.sfd = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)

        self.rfd.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
        self.sfd.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

        self.hops = []
        self.out_queue = []
        self.waiting = True
        self.deferred = defer.Deferred()

        reactor.addReader(self)
        reactor.addWriter(self)

        # send 1st probe packet
        self.out_queue.append(Hop(self.target, 1))

    def logPrefix(self):
        return "TracerouteProtocol(%s)" % self.target

    def fileno(self):
        return self.rfd.fileno()

    @defer.inlineCallbacks
    def hopFound(self, hop, ip, icmp):
        hop.remote_ip = ip
        hop.remote_icmp = icmp

        if (ip and icmp):
            hop.found = time.time()

        ttl = hop.ttl + 1
        last = self.hops[-2:]
        if (len(last) == 2 and last[0].remote_ip == ip) or \
           (ttl > (self.settings.get("max_hops", 30) + 1)):
            done = True
        else:
            done = False

        if not done:
            cb = self.settings.get("hop_callback")
            if callable(cb):
                yield defer.maybeDeferred(cb, hop)

        if not self.waiting:
            if self.deferred:
                self.deferred.callback(self.hops)
                self.deferred = None
        else:
            self.out_queue.append(Hop(self.target, ttl))

    def doRead(self):
        if not self.waiting or not self.hops:
            return

        pkt = self.rfd.recv(4096)
        # disassemble ip header
        ip = iphdr.disassemble(pkt[:20])

        if ip.proto != socket.IPPROTO_ICMP:
            return

        found = False

        # disassemble icmp header
        icmp = icmphdr.disassemble(pkt[20:28])
        if icmp.type == 0 and icmp.id == self.hops[-1].icmp.id:
            found = True
        elif icmp.type == 11:
            # disassemble referenced ip header
            ref = iphdr.disassemble(pkt[28:48])
            if ref.dst == self.target:
                found = True

        if ip.src == self.target:
            self.waiting = False

        if found:
            self.hopFound(self.hops[-1], ip, icmp)

    def hopTimeout(self, *ign):
        hop = self.hops[-1]
        if not hop.found:
            if hop.tries < self.settings.get("max_tries", 3):
                # retry
                self.out_queue.append(hop)
            else:
                # give up and move forward
                self.hopFound(hop, None, None)

    def doWrite(self):
        if self.waiting and self.out_queue:
            hop = self.out_queue.pop(0)
            pkt = hop.pkt
            if not self.hops or (self.hops and hop.ttl != self.hops[-1].ttl):
                self.hops.append(hop)

            self.sfd.sendto(pkt, (hop.ip.dst, 0))

            timeout = self.settings.get("timeout", 1)
            reactor.callLater(timeout, self.hopTimeout)

    def connectionLost(self, why):
        pass


def traceroute(target, **settings):
    tr = TracerouteProtocol(target, **settings)
    return tr.deferred


@defer.inlineCallbacks
def start_trace(target, **settings):
    hops = yield traceroute(target, **settings)
    last_hop = hops[-1]
    if settings["hop_callback"] is None:
        print(last_hop)

    reactor.stop()


def main(target):
    def show(hop):
        HOPS.append(str(hop))

    defaults = dict(hop_callback=show,
                    timeout=0.5,
                    max_tries=3,
                    max_hops=30)

    settings = defaults.copy()

    if os.getuid() != 0:
        print("traceroute needs root privileges for the raw socket")
        return []
    try:
        target = socket.gethostbyname(target)
    except Exception as e:
        print("could not resolve '{target}': {msg}".format(target, str(e)))
        return []

    reactor.callWhenRunning(start_trace, target, **settings)
    reactor.run()
    return HOPS

if __name__ == "__main__":
    main('guifi.net')
