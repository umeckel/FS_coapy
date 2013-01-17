# Copyright (c) 2010 People Power Co.
# All rights reserved.
# 
# This open source code was developed with funding from People Power Company
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# - Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.
# - Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the
#   distribution.
# - Neither the name of the People Power Corporation nor the names of
#   its contributors may be used to endorse or promote products derived
#   from this software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# ``AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE
# PEOPLE POWER CO. OR ITS CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
# STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
# OF THE POSSIBILITY OF SUCH DAMAGE
# 

COAP_PORT = 5683
"""The (TBR) IANA-assigned standard port for COAP services."""

RESPONSE_TIMEOUT = 2
"""The time, in seconds, to wait for an acknowledgement of a
confirmable message.

The inter-transmission time doubles for each retransmission."""

RESPONSE_RANDOM_FACTOR = 1.5
""" For a new confirmable message, the initial timeout is set
to a random number between RESPONSE_TIMEOUT and 
(RESPONSE_TIMEOUT * RESPONSE_RANDOM_FACTOR)"""

MAX_RETRANSMIT = 4
"""The number of retransmissions of confirmable messages to
non-multicast endpoints before the infrastructure assumes no
acknowledgement will be received."""

codes = { 0: 'EMPTY'
          1: 'GET',
          2: 'POST',
          3: 'PUT',
          4: 'DELETE',
          65: '2.01 Created',
          66: '2.02 Deleted',
          67: '2.03 Valid',
          68: '2.04 Changed',
          69: '2.05 Content',
          128: '4.00 Bad Request',
          129: '4.01 Unauthorized',
          130: '4.02 Bad Option',
          131: '4.03 Forbidden',
          132: '4.04 Not Found',
          133: '4.05 Method Not Allowed',
          134: '4.06 Not Acceptable',
          140: '4.12 Precondition Failed',
          141: '4.13 Request Entity Too Large',
          143: '4.15 Unsupported Media Type',
          160: '5.00 Internal Server Error',
          161: '5.01 Not Implemented',
          162: '5.02 Bad Gateway',
          163: '5.03 Service Unavailable',
          164: '5.04 Gateway Timeout',
          165: '5.05 Proxying Not Supported' }
#          40: '100 Continue',
#          80: '200 OK',
#          81: '201 Created',
#          124: '304 Not Modified',
#          160: '400 Bad Request',
#          164: '404 Not Found',
#          165: '405 Method Not Allowed',
#          175: '415 Unsupported Media Type',
#          200: '500 Internal Server Error',
#          202: '502 Bad Gateway',
#          204: '504 Gateway Timeout' }

EMPTY = 0
GET = 1
POST = 2
PUT = 3
DELETE = 4
CREATED = 65
DELETED = 66
VALID = 67
CHANGED = 68
CONTENT = 69
BAD_REQUEST = 128
UNAUTHORIZED = 129
BAD_OPTION = 130
FORBIDDEN = 131
NOT_FOUND = 132
METHOD_NOT_ALLOWED = 133
NOT_ACCEPTABLE = 134
PRECONDITION_FAILED = 140
REQUEST_ENTITY_TOO_LARGE = 141
UNSUPPORTED_MEDIA_TYPE = 143
INTERNAL_SERVER_ERROR = 160
NOT_IMPLEMENTED = 161
BAD_GATEWAY = 162
SERVICE_UNAVAILABLE = 163
GATEWAY_TIMEOUT = 164
PROXYING_NOT_SUPPORTED = 165
#CONTINUE = 40
#OK = 80
#CREATED = 81
#NOT_MODIFIED = 124
#BAD_REQUEST = 160
#NOT_FOUND = 164
#METHOD_NOT_ALLOWED = 165
#UNSUPPORTED_MEDIA_TYPE = 175
#INTERNAL_SERVER_ERROR = 200
#BAD_GATEWAY = 202
#GATEWAY_TIMEOUT = 204

media_types = { 0: 'text/plain',
                #1: 'text/xml',
                #2: 'text/csv',
                #3: 'text/html',
                #21: 'image/gif',
                #22: 'image/jpeg',
                #23: 'image/png',
                #24: 'image/tiff',
                #25: 'audio/raw',
                #26: 'video/raw',
                40: 'application/link-format',
                41: 'application/xml',
                42: 'application/octet-stream',
                #43: 'application/rdf+xml',
                #44: 'application/soap+xml',
                #45: 'application/atom+xml',
                #46: 'application/xmpp+xml',
                47: 'application/exi',
                #48: 'application/x-bxml',
                #49: 'application/fastinfoset',
                #50: 'application/soap+fastinfoset',
                50: 'application/json' }
"""A map from CoAP-assigned integral codes to Internet media type descriptions."""

media_types_rev = dict(zip(media_types.itervalues(), media_types.iterkeys()))
"""A map from Internet media type descriptions to the corresponding
CoAP-assigned integral code."""
