#!/usr/bin/python
# -*- coding: utf-8 -*-

# Ulrich Meckel
# s67703 Master Informatik
# 11 / 044 / 71-IK

import sys
import coapy
import coapy.link
import coapy.options
import coapy.connection
import socket
import getopt

ip = ''
port = coapy.COAP_PORT

try:
    opts, args = getopt.getopt(sys.argv[1:], 'vi:p:', [ 'verbose', '--ip=', '--port='])
    for (o, a) in opts:
        if o in ('-v', '--verbose'):
            verbose = True
        elif o in ('-i', '-ip'):
            ip = a
        elif o in ('-p', '--port'):
            port = int(a)

except getopt.GetoptError, e:
    print 'Option error: %s' % (e,)
    sys.exit(1)

bind_addr = (ip,port)

ep = coapy.connection.EndPoint(address_family=socket.AF_INET)
ep.bind(bind_addr)
    
_ressource = None

class DiscoverRessource(coapy.link.LinkValue):

    def __init__ (self, *args, **kw):
        global _ressource
        super(DiscoverRessource, self).__init__('/.well-known/core', ct=[coapy.media_types_rev.get('application/link-format')])
        _ressource = { self.uri : self }

    def add_Ressource (self, ressource):
        global _ressource
        _ressource[ressource.uri] = ressource

    def lookup (self, uri):
        return _ressource.get(uri)

    def process (self, rx_record):
        global _ressource
        msg = coapy.connection.Message(coapy.connection.Message.ACK, code=coapy.CONTENT, content_type='application/link-format')
        msg.payload = ",".join([ _r.encode() for _r in _ressource.itervalues() ])
        rx_record.ack(msg)

class GetRessource(coapy.link.LinkValue):
    

    def __init__(self,uri):
        coapy.link.LinkValue.__init__(self,uri)

        self._var = 'Init Value'

    def process (self, rx_record):
        rx_msg = rx_record.message

        if rx_msg.transaction_type == coapy.connection.Message.CON:
            msg = coapy.connection.Message(transaction_type=coapy.connection.Message.ACK) 
        else:
            msg = coapy.connection.Message(transaction_type=coapy.connection.Message.NON) 

        tok_opt = rx_msg.findOption(coapy.options.Token)
        if tok_opt != None:
            msg.addOption(tok_opt)

        if rx_msg.code != coapy.GET:
            msg.code=coapy.METHOD_NOT_ALLOWED
            rx_record.ack(msg)

        msg.payload = self._var
        msg.code=coapy.CONTENT
        rx_record.ack(msg)

class PutRessource(coapy.link.LinkValue):
    
    def __init__(self,uri):
        coapy.link.LinkValue.__init__(self,uri)

        self._var = 'Init Value'

    def process (self, rx_record):
        rx_msg = rx_record.message

        if rx_msg.transaction_type == coapy.connection.Message.CON:
            msg = coapy.connection.Message(transaction_type=coapy.connection.Message.ACK) 
        else:
            msg = coapy.connection.Message(transaction_type=coapy.connection.Message.NON) 

        tok_opt = rx_msg.findOption(coapy.options.Token)
        if tok_opt != None:
            msg.addOption(tok_opt)

        if rx_msg.code == coapy.GET:
            msg.payload = self._var
            msg.code=coapy.CONTENT
            rx_record.ack(msg)
        elif rx_msg.code == coapy.PUT:
            self._var = rx_msg.payload

            msg.code=coapy.CHANGED
            rx_record.ack(msg)
        else:
            msg.code=coapy.METHOD_NOT_ALLOWED
            rx_record.ack(msg)

   

CoAPServer = DiscoverRessource()
CoAPServer.add_Ressource(GetRessource('/getter'))
CoAPServer.add_Ressource(PutRessource('/putter'))


print 'Server Adresse',ep._get_address()
print 'Server Port',ep._get_port()

while True:
    rx_rec = ep.process(1000)
    if rx_rec is None:
        print 'No message recieve'
        continue
    print 'Message from',rx_rec.remote,'with ID',rx_rec.transaction_id,'recieved'
    msg = rx_rec.message
    if msg.transaction_type == msg.ACK:
        print 'Message of Type ACK'
    elif msg.transaction_type == msg.CON:
        print 'Message of Type CON'
    elif msg.transaction_type == msg.NON:
        print 'Message of Type NON'
    elif msg.transaction_type == msg.RST:
        print 'Message of Type RST'
    else:
        print 'Message Type Unknown (',msg.transaction_type,')'
        rx_rec.reset()

    if msg.code == coapy.GET:
        print 'GET Message on URI',msg.build_uri()
    elif msg.code == coapy.DELETE:
        print 'DELETE Message on URI',msg.build_uri()
    elif msg.code == coapy.POST:
        print 'POST Message on URI',msg.build_uri()
    elif msg.code == coapy.PUT:
        print 'PUT Message on URI',msg.build_uri()
    else:
        print 'Message Code Unknown (',msg.code,') on',msg.build_uri()
        rx_rec.reset()

    print 'Options'
    for otypelist in msg.options:
        for o in otypelist:
            print o
            print o.value
    uri = msg.findOption(coapy.options.UriPath)
    if uri is None:
        continue
    uripath = ''
    for pathpiece in uri:
        uripath = uripath+'/'+pathpiece.value
    print uripath
    res = CoAPServer.lookup(uripath)
    if res is None:
        print 'URI',uripath,'not supported'
        rx_rec.reset()
        continue

    res.process(rx_rec)
