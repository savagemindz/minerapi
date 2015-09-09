# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod, abstractproperty
import socket
import json


class Miner(object):
    """ Common API operations """

    __metaclass__ = ABCMeta

    def __init__(self, host='localhost', port=None):
        self.host = host
        if port is not None:
            self.port = port

    @abstractmethod
    def _format(self, command, args):
        pass

    @abstractmethod
    def _parse(self, data):
        pass

    @abstractproperty
    def _commands(self):
        pass

    def json(self, data):

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            sock.connect((self.host, self.port))
            sock.send(data)
            received = self._receive(sock)
        finally:
            try:
                sock.shutdown(socket.SHUT_RDWR)
            except socket.error:
                pass
            sock.close()

        return received[:-1]

    def command(self, command, *args):
        """ Send a command (a json encoded dict) and
        receive the response (and decode it).
        """
        return self._parse(self.json(self._format(command, args)))

    def _receive(self, sock, size=4096):
        msg = ''
        while 1:
            chunk = sock.recv(size)
            if chunk:
                msg += chunk
            else:
                break
        return msg

    def __dir__(self):
        return self._commands

    def __getattr__(self, attr):
        """ Allow us to make command calling methods.

        >>> miner = Miner()
        >>> miner.summary()

        """
        def out(*args):
            return self.command(attr, *args)
        return out


class Cgminer(Miner):
    """ Cgminer RPC API wrapper """

    port = 4028
    _commands = [
        'version', 'config', 'summary', 'pools', 'devs', 'edevs',
        'pga', 'pgacount',
        'switchpool', 'enablepool', 'addpool', 'poolpriority', 'poolquota',
        'disablepool', 'removepool',
        'save', 'quit', 'notify', 'privileged',
        'pgaenable', 'pgadisable', 'pgaidentify', 'devdetails', 'restart',
        'stats', 'estats', 'check', 'coin', 'debug', 'setconfig',
        'usbstats', 'pgaset', 'zero', 'hotplug',
        'asc', 'ascenable', 'ascdisable', 'ascidentify', 'asccount',
        'ascset', 'lcd', 'lockstats'
    ]

    def _format(self, command, args):
        payload = {"command": command}
        if args:
            arg = ",".join(map(str, args))
            # Parameter must be converted to basestring (no int)
            payload.update({'parameter': unicode(arg)})

        return json.dumps(payload)

    def _parse(self, data):
        return json.loads(data)

    def failover_only(self, switch):
        return self.command('failover-only', 'true' if switch else 'false')


class Bfgminer(Cgminer):
    _commands = list(set(Cgminer._commands).union([
        'procs', 'devscan', 'proc', 'proccount', 'pgarestart',
        'procenable', 'procdisable', 'procidentify', 'procset'
    ]) - set([
        'usbstats', 'estats',
        'asc', 'ascenable', 'ascdisable', 'ascidentify', 'asccount',
        'ascset', 'lcd', 'lockstats'
    ]))
