import sys
import getopt
import coapy.connection
import time
import socket

#python coapput.py --host bbbb::ff:fe00:2222 --port 5683 -6 --uri-path /leds --payload=mode=abc
#python coapput.py --host 127.0.0.1 --port 5683 -4 --uri-path /putter --payload=inhalt

uri_path = 'sink'
host = 'ns.tzi.org'
port = 61616
verbose = False
payload = ''
try:
    opts, args = getopt.getopt(sys.argv[1:], 'd:46u:h:p:v', [ 'payload=','ipv4','ipv6','uri-path=', 'host=', 'port=', 'verbose' ])
    for (o, a) in opts:
        if o in ('-u', '--uri-path'):
            uri_path = a
        elif o in ('-h', '--host'):
            host = a
        elif o in ('-p', '--port'):
            port = int(a)
        elif o in ('-v', '--verbose'):
            verbose = True
        elif o in ('-4', '--ipv4'):
            address_family = socket.AF_INET
        elif o in ('-6', '--ipv6'):
            address_family = socket.AF_INET6
        elif o in ('-d', '--payload'):
            payload = a
except getopt.GetoptError, e:
    print 'Option error: %s' % (e,)
    sys.exit(1)

if socket.AF_INET == address_family:
    remote = (host, port)
elif socket.AF_INET6 == address_family:
    remote = (host, port, 0, 0)
ep = coapy.connection.EndPoint(address_family=address_family)
ep.socket.bind(('', coapy.COAP_PORT+1))

def wait_for_response (ep, txr):
    global verbose
    
    while True:
        rxr = ep.process(1000)
        if rxr is None:
            print 'No message received; waiting'
            continue
        if verbose:
            print rxr.message
            print "\n".join(['  %s' % (str(_o),) for _o in rxr.message.options])
            print '  %s' % (rxr.message.payload,)
        if rxr.pertains_to != txr:
            print 'Irrelevant; waiting'
            continue
        return rxr.message

def getResource (ep, uri_path, remote):
    msg = coapy.connection.Message(code=coapy.GET, uri_path=uri_path)
    resp = wait_for_response(ep, ep.send(msg, remote))
    return resp.payload

def putResource (ep, uri_path, remote, value):
    print 'send code=',coapy.PUT
    msg = coapy.connection.Message(code=coapy.PUT, payload=value, uri_path=uri_path)
    resp = wait_for_response(ep, ep.send(msg, remote))
    return resp.payload

data = getResource(ep, uri_path, remote)
print 'Initial setting: %s' % (data,)
#new_data = 'hello %s' % (time.time(),)
new_data = a
print 'Put value: %s' % (new_data,)
resp = putResource(ep, uri_path, remote, new_data)
print 'Put returned: %s' % (resp,)
data = getResource(ep, uri_path, remote)
print 'Get returned: %s' % (data,)
