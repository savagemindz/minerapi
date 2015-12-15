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


class MinerException(Exception):
    pass


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
            arg = ",".join(map(
                lambda arg:
                str(arg).replace('\\','\\\\').replace(',','\\,'),
                args
            ))
            # Parameter must be converted to basestring (no int)
            payload.update({'parameter': unicode(arg)})

        return json.dumps(payload)

    def _parse(self, data):
        return json.loads(data)

    def failover_only(self, switch):
        return self.command('failover-only', 'true' if switch else 'false')

    def command(self, command, *args):
        response = super(Cgminer, self).command(command, *args)
        try:
            values = response[command.upper()]
        except KeyError:
            status = response.pop('STATUS')[0]
            if status['STATUS'] in ('E', 'F'):
                raise MinerException(status['Msg'])
            else:
                try:
                    values = response[
                        filter(lambda k: k != 'id', response)[0]]
                except IndexError:
                    return
        if len(values) > 1 or command[-1] == 's':
            return values

        value = values[0]
        return value if len(value) > 1 else value.values()[0]


class Bfgminer(Cgminer):
    _commands = list(set(Cgminer._commands).union([
        'procs', 'devscan', 'proc', 'proccount', 'pgarestart',
        'procenable', 'procdisable', 'procidentify', 'procset'
    ]) - set([
        'usbstats', 'estats',
        'asc', 'ascenable', 'ascdisable', 'ascidentify', 'asccount',
        'ascset', 'lcd', 'lockstats'
    ]))


class Cpuminer(Miner):
    port = 4048
    _commands = ['summary', 'threads', 'seturl', 'quit']

    def _format(self, command, args):
        return command

    def _parse(self, data):
        def split_key_value(word):
            key, value = word.split('=')
            try:
                val = (float if '.' in value else int)(value)
            except ValueError:
                val = value
            return key, val

        return [
            dict(split_key_value(item) for item in part.split(';'))
            for part in data.split('|') if part
        ]

    def _super_json(self, data):
        return self._parse(super(Cpuminer, self).json(data))

    def json(self, data):
        return json.dumps(self._super_json(data))

    def command(self, command, *args):
        values = self._super_json(self._format(command, args))
        if not values:
            raise MinerException('No answer')

        return values if len(values) > 1 or command[-1] == 's' \
            else values[0]
