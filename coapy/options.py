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

"""Classes and functions related to CoAP header options.
"""
import coapy.constants
import types
import struct
import binascii
import collections

OPTION_TYPE_FENCEPOST = 14
# TODO: QUICKFIX for unordered set in option.decode()
# http://stackoverflow.com/questions/1653970/does-python-have-an-ordered-set
# http://code.activestate.com/recipes/576694/
class OrderedSet(collections.MutableSet):

    def __init__(self, iterable=None):
        self.end = end = [] 
        end += [None, end, end]         # sentinel node for doubly linked list
        self.map = {}                   # key --> [key, prev, next]
        if iterable is not None:
            self |= iterable

    def __len__(self):
        return len(self.map)

    def __contains__(self, key):
        return key in self.map

    def add(self, key):
        if key not in self.map:
            end = self.end
            curr = end[1]
            curr[2] = end[1] = self.map[key] = [key, curr, end]

    def discard(self, key):
        if key in self.map:        
            key, prev, next = self.map.pop(key)
            prev[2] = next
            next[1] = prev

    def __iter__(self):
        end = self.end
        curr = end[2]
        while curr is not end:
            yield curr[0]
            curr = curr[2]
    def __reversed__(self):
        end = self.end
        curr = end[1]
        while curr is not end:
            yield curr[0]
            curr = curr[1]

    def pop(self, last=True):
        if not self:
            raise KeyError('set is empty')
        key = self.end[1][0] if last else self.end[2][0]
        self.discard(key)
        return key

    def __repr__(self):
        if not self:
            return '%s()' % (self.__class__.__name__,)
        return '%s(%r)' % (self.__class__.__name__, list(self))

    def __eq__(self, other):
        if isinstance(other, OrderedSet):
            return len(self) == len(other) and list(self) == list(other)
        return set(self) == set(other)

def length_of_vlint (value):
    """
    :param value: Any non-negative integral value
    :returns: Determine the number of octets required to express *value* as by
        :func:`pack_vlint`.
    :rtype: :class:`int`
    """
    octets = 1
    while (1 << (8 * octets)) <= value:
        octets += 1
    return octets

def pack_vlint (value):
    """Pack an integer into a string.

    CoAP variable-length integers are packed into a sequence of octets
    in network byte order.  Leading octets that would have a zero
    value are elided.

    :param value: Any non-negative integral value
    :rtype: :class:`str`
    """
    
    octets = []
    while 0 != value:
        octets.insert(0, chr(value & 0xFF))
        value = value / 256
    if 0 == len(octets):
        octets.append(chr(0))
    return ''.join(octets)

def unpack_vlint (packed):
    """Extract an integer from a string as created by :func:`pack_vlint`.
    
    :param packed: A string of octets containing a packed integer.
    :rtype: :class:`int`
    """
    value = 0
    for c in packed:
        value = (value * 256) + ord(c)
    return value

def option_type_is_elective (type_val):
    """
    :param type_val: the integral type value for an option
    :return: ``True`` iff an option of Type *type_val* is elective (can be skipped if unrecognized).
    """

    return 0 == (type_val & 0x01)

class _Base (object):
    """Base class for all CoAPy option classes.
    """

    Type = None
    """The type code for the option.

    Options with an even type code are elective, while those with an
    odd type code are critical.

    :note: This value is overridden in each class that implements a CoAP option.
    """

    Name = None
    """The standardized name of the option.

    :note: This value is overridden in each class that implements a CoAP option.
    """

    Default = None
    """The default value of the option.  ``None`` if the option has no default.

    :note: This value is overridden in each class that implements a
           CoAP option with a default value.
    """

    Repeatable = False
    """The most Options are not Repeatable. This means they can occur only once
        in a Message

    :note: This value is overridden in each class that can occur multiple times
            in a Message
    """

    value = property()
    """The option value.

    Python objects and type instances assigned as option values are
    validated within the limitations of the CoAP option's packed
    representation.  For example, assigning to an instance of
    :class:`UriPath<coapy.options.UriPath>` a value that exceeds the
    :attr:`length
    limitation<coapy.options._StringValue_mixin.MAX_VALUE_LENGTH>` of
    270 will result in a :exc:`ValueError`.

    In cases where the option value is expected to have an
    IANA-assigned significance but the specific assigned value is
    unrecognized, the value assignment is permitted if doing so does
    not violate the requirements of the packed option representation.
    For example, assigning a value of ``15`` to an instance of
    :class:`ContentType<coapy.options.ContentType>` would be allowed, though the
    value 15 is not (currently) associated with a specific media type.
    """

    length = property()
    """The length, in octets, of the packed option.

    :note: This is a read-only property."""
    
    packed = property()
    """The sequence of octets representing the option value in packed
    form (i.e., as it appears within an option header).

    The sequence does not include the option delta or length, only the
    value.

    :note: This is a read-only property.

    :see: :meth:`unpack<coapy.options._Base.unpack>`
    
    """

    @classmethod
    def unpack (cls, packed):
        """Create an instance of this option from a packed representation.

        :param packed: A sequence of octets representing the option
           value, exclusive of the option type and length.

        :rtype: An instance of the leaf class.

        :see: :attr:`packed<coapy.options._Base.packed>`

        """
        return cls(packed)

    def __init__ (self, value=None):
        if value is None:
            value = self.Default
        self._setValue(value)

    @classmethod
    def is_critical (cls):
        """Return ``True`` if this option must be understood."""
        return cls.Type & 0x01

    def is_default (self):
        """Return ``True`` iff the current value of the option is
        equal to the default value of the option.

        This is used by :func:`encode<coapy.options.encode>` to avoid unnececessarily packing options.
        """
        
        return self.Default == self.value

    def __str__ (self):
        return '%s: %s' % (self.Name, self.value)

class _StringValue_mixin (object):
    """Mix-in to support options with octet-sequence values.
    """
    
    MAX_VALUE_LENGTH = 270
    """The maximum length, in octets, for the option value."""

    MIN_VALUE_LENGTH = 0
    """The minimum length, in octets, for the option value."""

    def _setValue (self, value):
        if not isinstance(value, types.StringTypes):
            raise ValueError(value)
        if (self.MIN_VALUE_LENGTH > len(value)) or (self.MAX_VALUE_LENGTH < len(value)):
            raise ValueError(value)
        self._value = value

    value = property(lambda _s: _s._value,
                     _setValue)
    """Overrides the base :attr:`value<coapy.options._Base.value>`
    property.  The assigned value must be a string within the limits
    of
    :attr:`MIN_VALUE_LENGTH<coapy.options._StringValue_mixin.MIN_VALUE_LENGTH>`
    and
    :attr:`MAX_VALUE_LENGTH<coapy.options._StringValue_mixin.MAX_VALUE_LENGTH>`
    for the option class."""

    length = property(lambda _s: len(_s._value))

    packed = property(lambda _s: _s._value)

class _UriPath_mixin (_StringValue_mixin):
    """Mix-in to support options with string values that represent URIs."""

    def _setValue (self, value):
        if not isinstance(value, types.StringTypes):
            raise ValueError(value)
        if value.startswith('/'):
            raise ValueError(value)
        return super(_UriPath_mixin, self)._setValue(value)

    value = property(lambda _s: _s._value,
                     _setValue)
    """Overrides the string :attr:`value<coapy.options._StringValue_mixin.value>` property.
    In addition to length limitations, the assigned value must not
    start with a forward-slash."""

class _IntegerValue_mixin (object):
    """Mix-in to support options with integral values."""

    MIN_VALUE = 0
    """The minimum allowable value for the option."""
    
    MAX_VALUE = 0xFFFFFFFF
    """The maximum allowable value for the option."""
    
    @classmethod
    def unpack (cls, packed):
        return cls(unpack_vlint(packed))

    def _setValue (self, value):
        value = int(value)
        if (self.MIN_VALUE > value) or (self.MAX_VALUE < value):
            raise ValueError(value)
        self._value = value

    value = property(lambda _s: _s._value,
                     _setValue)
    """Overrides the base :attr:`value<coapy.options._Base.value>`
    property.  The assigned value must be an integral value within the
    limits of
    :attr:`MIN_VALUE<coapy.options._IntegerValue_mixin.MIN_VALUE>` and
    :attr:`MAX_VALUE<coapy.options._IntegerValue_mixin.MAX_VALUE>` for
    the option class."""


    length = property(lambda _s: length_of_vlint(_s._value))

    packed = property(lambda _s: pack_vlint(_s._value))

# There is no UriScheme Option in coap-08 ? But also not in 03 ?
#class UriScheme (_StringValue_mixin, _Base):
#    """The schema part of the URI."""
#    
#    Type = 3
#    Name = 'Uri-Scheme'
#    Default = 'coap'
#    """The default URI scheme is ``coap``."""
#    
#    _value = Default

# There is no UriAuthority Option in coap-08 anymore
# its split into Uri-Host and Uri-Port
#class UriAuthority (_StringValue_mixin, _Base):
#    """The authority (host+port) part of the URI."""
#    
#    Type = 5
#    Name = 'Uri-Authority'
#    Default = ''
#    """By default, the URI authority is empty."""
#    
#    _value = Default

class ContentType (_Base):
    """The Internet media type describing the message body."""

    Type = 1
    Name = 'Content-type'
    Default = None
    """There is no default Content Type anymore in coap-08."""

    _value = Default

    def _setValue (self, value):
        value = int(value)
        if (0 > value) or (65535 < value):
            raise ValueError(value)
        self._value = value

    def _setValueAsString (self, value_as_string):
        value = coapy.constants.media_types_rev.get(value_as_string)
        if value is None:
            raise ValueError(value_as_string)
        self._value = value

    def __init__ (self, value=None):
        if value is None:
            value = self.Default
        if isinstance(value, types.StringTypes):
            self._setValueAsString(value)
        else:
            self._setValue(value)

    @classmethod
    def unpack (cls, packed):
        if len(packed) == 0:
            return cls(0)
        return cls(struct.unpack('B', packed)[0])

    #:
    # Stupid Sphinx assigns this a documentation string of "B" because of the lambda expression.
    packed = property(lambda _s: struct.pack('B', _s._value))

    value = property(lambda _s : _s._value,
                     _setValue)

    value_as_string = property(lambda _s : coapy.constants.media_types[_s._value],
                     _setValueAsString)
    """Access the value using its IANA-assigned media type encoding
    scheme, e.g. ``application/xml``.

    :note: Only media types that have been assigned CoAP integral
           values are allowed.
    """

    length = property(lambda _s: 1)
    
    def __str__ (self):
        return '%s: %s' % (self.Name, self.value_as_string)

class MaxAge (_IntegerValue_mixin, _Base):
    """The maximum age of a resource for use in cache control, in seconds."""
    Type = 2
    Name = 'Max-age'
    Default = 60

class ProxyUri (_UriPath_mixin, _Base):
    """The Proxy-Uri Option is used to make a request to a proxy (see               
   Section 5.7).  The proxy is requested to forward the request or              
   service it from a valid cache, and return the response.                      
                                                                                
   #TODO
   The option value is an absolute-URI ([RFC3986], Section 4.3).  In            
   case the absolute-URI doesn't fit within a single option, the Proxy-         
   Uri Option MAY be included multiple times in a request such that the         
   concatenation of the values results in the single absolute-URI."""

    Type = 3
    Name = 'Proxy-Path'
    Default = None

    _value = Default

class Etag (_StringValue_mixin, _Base):
    """An opaque sequence of bytes specifying the version of resource representation."""
    
    Type = 4
    Name = 'ETag'
    Default = None
    Repeatable = True

    MIN_VALUE_LENGTH = 1
    """An ETag value :attr:`must have at least one octet<coapy.options._StringValue_mixin.MIN_VALUE_LENGTH>`."""

    MAX_VALUE_LENGTH = 8
    """An ETag value :attr:`cannot exceed eight octets in length<coapy.options._StringValue_mixin.MAX_VALUE_LENGTH>`."""

class UriHost (_StringValue_mixin, _Base):
    """The Uri-Host, Uri-Port, Uri-Path and Uri-Query Options are used to
    specify the target resource of a request to a CoAP origin server.

    The Uri-Host Option specifies the Internet host of the resource           
    being requested"""

    Type = 5
    Name = 'Uri-Host'
    Default = ''

    _value = Default

class LocationPath (_UriPath_mixin, _Base):
    """ The Location-Path indicates the location of a resource as an 
    absolute path URI. The Location-Path Option is          
   similar to the Uri-Path Option.

    Normally used in in a response to indicate the location of a newly
    created resource."""
    
    Type = 6
    Name = 'Location-Path'
    Default = None
    Repeatable = True

class UriPort (_IntegerValue_mixin, _Base):
    """The Uri-Host, Uri-Port, Uri-Path and Uri-Query Options are used to 
   specify the target resource of a request to a CoAP origin server.       
   The options encode the different components of the request URI in a
   way that no percent-encoding is visible in the option values and that
   the full URI can be reconstructed at any involved end-point."""

    Type = 7
    Name = 'Uri-Port'
    MAX_VALUE = 0xFFFF
    """An Uri-Port value :attr:`cannot exceed two octets in length<coapy.options._IntegerValue_mixin.MAX_VALUE>`."""

class LocationQuery (_UriPath_mixin, _Base):
    """ The Location-Path and Location-Query Options indicates the location
    of a resource as an absolute path URI.  The Location-Query Option similar 
    to the Uri-Query Option.

    Normally used in in a response to indicate the location of a newly
    created resource."""
    
    Type = 8
    Name = 'Location-Query'
    Default = None
    Repeatable = True

class UriPath (_StringValue_mixin, _Base):
    """The Uri-Host, Uri-Port, Uri-Path and Uri-Query Options are used to
    specify the target resource of a request to a CoAP origin server.
     
    Each Uri-Path Option specifies one segment of the absolute path to
    the resource."""


    Type = 9
    Name = 'Uri-Path'
    Default = None
    Repeatable = True

    _value = Default

class Token (_StringValue_mixin, _Base):
    """A client-generared Token represented as opaque sequence of bytes."""
    
    Type = 11
    Name = 'Token'
    Default = None

    MIN_VALUE_LENGTH = 1
    """A Token value :attr:`must have at least one octet<coapy.options._StringValue_mixin.MIN_VALUE_LENGTH>`."""

    MAX_VALUE_LENGTH = 8
    """A Token value :attr:`cannot exceed eight octets in length<coapy.options._StringValue_mixin.MAX_VALUE_LENGTH>`."""

class Accept (_IntegerValue_mixin, _Base):
    """The CoAP Accept option indicates when included one or more times in a
    request, one or more media types, each of which is an acceptable
    media type for the client, in the order of preference."""

    Type = 12
    Name = 'Accept'
    Default = None
    Repeatable = True
    MAX_VALUE = 0xFFFF
    """An Accept value :attr:`cannot exceed two octets in length<coapy.options._IntegerValue_mixin.MAX_VALUE>`."""

class IfMatch (_StringValue_mixin, _Base):
    """The value of an If-Match option is either an ETag or the empty
    string.  An empty string places the precondition on the existence of
    any current representation for the target resource."""
    
    Type = 13
    Name = 'If-Match'
    Default = None
    Repeatable = True

    MIN_VALUE_LENGTH = 0
    """A If-Match value :attr:`must have at least one octet<coapy.options._StringValue_mixin.MIN_VALUE_LENGTH>`."""

    MAX_VALUE_LENGTH = 8
    """A If-Match value :attr:`cannot exceed eight octets in length<coapy.options._StringValue_mixin.MAX_VALUE_LENGTH>`."""

class UriQuery (_StringValue_mixin, _Base):
    """The Uri-Host, Uri-Port, Uri-Path and Uri-Query Options are used to
    specify the target resource of a request to a CoAP origin server.
     
    each Uri-Query Option specifies one argument parameterizing the
    resource.
    """


    Type = 15
    Name = 'Uri-Query'
    Default = None
    Repeatable = True

    _value = Default

class IfNoneMatch (_Base):
    """If the target resource does exist, then the server MUST NOT perform
    the requested method.  Instead, the server MUST respond with the 4.12
    (Precondition Failed) response code.
    """
    Type = 21
    Name = 'If-None-Match'
    Default = None

    _value = Default


# TODO Observe Option

# The Block Option ( draft-ietf-core-block-04 )
# Request 
#   Block1(PUT/POST)
#       Identified the sending block 
#       M == 1 - Payload is Size of Power of two given by blocksize
#       M == 0 Last block ( must not have this size )
#   Block2(GET)
#       Request a specific block (identified by block number)
#       M bit MUST set to zero
# Response
#   Block1(PUT/POST)
#       Indicates what block number is being acknowledged
#       Also send the preferred Block size
#   Block2
#       Identified the recieving block(GET)
#       M == 1 - Payload is Size of Power of two given by blocksize
#       M == 0 Last block ( must not have this size )
#       
class _Block (_Base):
    """Support block-wise transfers of large resources.

    :warning: This is an experimental option.  See `draft-bormann-core-misc <http://tools.ietf.org/html/draft-bormann-coap-misc>`_
    """
    
    Type = None
    Name = '_Block'
    Default = 0

    MIN_SIZE_EXPONENT = 4
    """The minimum supported size for resource blocks is 2^4 or 16 octets."""

    MAX_SIZE_EXPONENT = 10
    """The maximum supported size for resource blocks is 2^11 or 2048 octets."""

    def _calculate_value (self):
        v = self.__blockNumber << 4
        if self.__more:
            v += 0x08
        v += 0x07 & (self.__sizeExponent - 4)
        return v

    def __init__ (self, block_number=0, more=False, size_exponent=7):
        """
        :param block_number: The number of the block

        :param more: A :class:`bool` used in response messages to
           indicate the resource has additional blocks with higher
           block numbers.

        :param size_exponent: The base-2 exponent for the block size.
          The minimum exponent supported is 4 (a 16-octet block); the
          maximum is 11 (a 2048-octet block).
        """
        self.__blockNumber = int(block_number)
        self.__more = not not more
        self.__sizeExponent = int(size_exponent)
        if (self.MIN_SIZE_EXPONENT > self.__sizeExponent) or (self.MAX_SIZE_EXPONENT < self.__sizeExponent):
            raise ValueError()

    @classmethod
    def unpack (cls, packed):
        v = unpack_vlint(packed)
        return cls(block_number=(v >> 4), more=bool(0x08 & v), size_exponent=4 + (0x07 & v))

    def _get_block_number (self):
        """The block number, starting at zero for the first block."""
        return self.__blockNumber
    block_number = property(_get_block_number)

    def _get_more (self):
        """``True`` iff there are subsequent blocks in the resource."""
        return self.__more
    more = property(_get_more)

    def _get_size_exponent (self):
        """The base-2 exponent defining the size of each (non-final) block.

        See :attr:`.MIN_SIZE_EXPONENT` and :attr:`.MAX_SIZE_EXPONENT`.
        """
        return self.__sizeExponent
    size_exponent = property(_get_size_exponent)

    value = property(_calculate_value)
    length = property(lambda _s: length_of_vlint(_s.value))
    packed = property(lambda _s: pack_vlint(_s.value))

    def __str__ (self):
        return '%s: blk=%d, m=%d, sze=%d' % (self.Name, self.__blockNumber, self.__more, self.__sizeExponent)

class Block1 (_Block):
    Type = 19
    Name = 'Block1'
class Block2 (_Block):
    Type = 17
    Name = 'Block2'

class UnrecognizedOptionError (Exception):
    def __init__ (self, option_type, option_value):
        self.option_type = option_type
        self.option_value = option_value
        super(UnrecognizedOptionError, self).__init__()

    def __str__ (self):
        return '%s: type=%d, value=%s' % (self.__class__.__name__, self.option_type, binascii.hexlify(self.option_value))

# TODO FS_coapy (MAYBE DONE)
def encode (options, ignore_if_default=True):
    """Encode a set of CoAP options for transmission.

    The options are sorted as required by CoAP.  The return value is a
    pair (*num_options*, *packed*) where *num_options* is the number
    of options that were encoded, and *packed* is the octet sequence
    encoding those options.

    :param options: An iterable of option instances

    :param ignore_if_default: If ``True``, any option instance that
        has the default value for the option is excluded from the packed
        representation.
    :return: (*num_options*, *packed_options*)
    :rtype: (:class:`int`, :class:`str`)
    :raises: :exc:`Exception` if a packed option exceeds the representable option length
    """
    option_list = sorted(options, lambda _a,_b: cmp(_a[0].Type, _b[0].Type))
    packed_pieces = []
    type_val = 0
    MAX_DELTA = 15
    OVER_LENGTH = 15
    num_options = 0
    for optiontypelist in option_list:
        for opt in optiontypelist:
            if opt.is_default() and ignore_if_default:
                continue
            delta = opt.Type - type_val
            while MAX_DELTA < delta:
                # Which Fencepost Option did we finally need? (14,28,42,...)
                fencepost = (OPTION_TYPE_FENCEPOST * int((opt.Type + OPTION_TYPE_FENCEPOST - 1) / OPTION_TYPE_FENCEPOST)) - 1
                # fp_multiplier (14 => 1,28 => 2,3 => 42,...)
                fp_multiplier = fencepost / OPTION_TYPE_FENCEPOST
                fp_delta = fencepost - type_val
                # Did we need a intermediate Fencepost Option ?
                while fp_delta > MAX_DELTA:
                    fp_multiplier = fp_multiplier - 1
                    fencepost = fp_multiplier * OPTION_TYPE_FENCEPOST
                    fp_delta = fencepost - type_val

                # Option with delta fp_delta and length 0 (empty) 
                packed_pieces.append(chr(fp_delta << 4))
                num_options += 1
                type_val = fencepost
                delta = opt.Type - type_val
            length = opt.length
            if OVER_LENGTH <= length:
                length -= OVER_LENGTH
                if 255 < length:
                    raise Exception('Option length too large')
                packed_pieces.append(chr((delta << 4) + OVER_LENGTH) + chr(length))
            else:
                packed_pieces.append(chr((delta << 4) + length))
            packed_pieces.append(opt.packed)
            type_val += delta
            num_options += 1
    return (num_options, ''.join(packed_pieces))

# TODO FS_coapy (Nothing Change here?)
def decode (num_options, payload):
    """Decode a set of CoAP options and extract a message body.

    The specified number of options are pulled from the initial octets
    of the payload, and converted into instances of the corresponding
    option class.  The return value is a pair (*options*, *body*)
    where *options* is a list of all recognized options in their order
    of appearance and *body* is the remainder of the payload after
    options have been stripped.

    :param num_options: The number of options to be extracted.
    :param payload: The packed options followed by an optional message body.
    :return: (*options*, *body*)
    :rtype: (:class:`list`, :class:`str`)
    :raises: :exc:`Exception` if an unrecognized critical option is encountered
    """

    type_val = 0
    options = OrderedSet()
    while 0 < num_options:
        num_options -= 1
        value_start_index = 1
        odl = ord(payload[0])
        type_val += (odl >> 4)
        length = odl & 0x0F
        if 15 == length:
            length += ord(payload[value_start_index])
            value_start_index += 1
        value_end_index = value_start_index + length
        # Skip Fencepost Option
        if 0 != (type_val % OPTION_TYPE_FENCEPOST):
            option_class = Registry.get(type_val)
            if option_class is not None:
                options.add(option_class.unpack(payload[value_start_index:value_end_index]))
            elif not option_type_is_elective(type_val):
                raise UnrecognizedOptionError(type_val, payload[value_start_index:value_end_index])
        payload = payload[value_end_index:]
    return (options, payload)

Registry = { }
"""A map from integral option types to the Python class that implements the option."""

#for _opt in (ContentType, UriScheme, UriAuthority, UriPath,
#            Location, MaxAge, Etag, Block):
for _opt in (ContentType,MaxAge,ProxyUri,Etag,UriHost,LocationPath,
             UriPort,LocationQuery,UriPath,Token,Accept,IfMatch,
             UriQuery,IfNoneMatch,Block1,Block2):
    Registry[_opt.Type] = _opt

