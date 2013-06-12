###############################################################################
##
##  Copyright 2013 Tavendo GmbH
##
##  Licensed under the Apache License, Version 2.0 (the "License");
##  you may not use this file except in compliance with the License.
##  You may obtain a copy of the License at
##
##      http://www.apache.org/licenses/LICENSE-2.0
##
##  Unless required by applicable law or agreed to in writing, software
##  distributed under the License is distributed on an "AS IS" BASIS,
##  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
##  See the License for the specific language governing permissions and
##  limitations under the License.
##
###############################################################################

__all__ = ["PerMessageBzip2Mixin",
           "PerMessageBzip2Offer",
           "PerMessageBzip2Accept",
           "PerMessageBzip2Response",
           "PerMessageBzip2"]


import bz2

from compress_base import PerMessageCompressOffer, \
                          PerMessageCompressAccept, \
                          PerMessageCompressResponse, \
                          PerMessageCompress


class PerMessageBzip2Mixin:
   """
   Mixin class for this extension.
   """

   EXTENSION_NAME = "permessage-bzip2"
   """
   Name of this WebSocket extension.
   """

   COMPRESS_LEVEL_PERMISSIBLE_VALUES = [1, 2, 3, 4, 5, 6, 7, 8, 9]
   """
   Permissible value for compression level parameter.
   """



class PerMessageBzip2Offer(PerMessageCompressOffer, PerMessageBzip2Mixin):
   """
   Set of extension parameters for `permessage-bzip2` WebSocket extension
   offered by a client to a server.
   """

   @classmethod
   def parse(Klass, params):
      """
      Parses a WebSocket extension offer for `permessage-bzip2` provided by a client to a server.

      :param params: Output from :method:`autobahn.websocket.WebSocketProtocol._parseExtensionsHeader`.
      :type params: list

      :returns: object -- A new instance of :class:`autobahn.compress.PerMessageBzip2Offer`.
      """
      ## extension parameter defaults
      ##
      acceptMaxCompressLevel = False
      requestMaxCompressLevel = 0

      ##
      ## verify/parse c2s parameters of permessage-bzip2 offer
      ##
      for p in params:

         if len(params[p]) > 1:
            raise Exception("multiple occurence of extension parameter '%s' for extension '%s'" % (p, Klass.EXTENSION_NAME))

         val = params[p][0]

         if p == 'c2s_max_compress_level':
            if val != True:
               raise Exception("illegal extension parameter value '%s' for parameter '%s' of extension '%s'" % (val, p, Klass.EXTENSION_NAME))
            else:
               acceptMaxCompressLevel = True

         elif p == 's2c_max_compress_level':
            if val not in ['1', '2', '3', '4', '5', '6', '7', '8', '9']:
               raise Exception("illegal extension parameter value '%s' for parameter '%s' of extension '%s'" % (val, p, Klass.EXTENSION_NAME))
            else:
               requestMaxCompressLevel = int(val)

         else:
            raise Exception("illegal extension parameter '%s' for extension '%s'" % (p, Klass.EXTENSION_NAME))

      offer = Klass(acceptMaxCompressLevel,
                    requestMaxCompressLevel)
      return offer


   def __init__(self,
                acceptMaxCompressLevel = True,
                requestMaxCompressLevel = 0):
      """
      Constructor.

      :param acceptMaxCompressLevel: Iff true, client accepts "maximum compression level" parameter.
      :type acceptMaxCompressLevel: bool
      :param requestMaxCompressLevel: Iff non-zero, client requests given "maximum compression level" - must be 1-9.
      :type requestMaxCompressLevel: int
      """
      if type(acceptMaxCompressLevel) != bool:
         raise Exception("invalid type %s for acceptMaxCompressLevel" % type(acceptMaxCompressLevel))

      self.acceptMaxCompressLevel = acceptMaxCompressLevel

      if requestMaxCompressLevel != 0 and requestMaxCompressLevel not in self.COMPRESS_LEVEL_PERMISSIBLE_VALUES:
         raise Exception("invalid value %s for requestMaxCompressLevel - permissible values %s" % (requestMaxCompressLevel, self.COMPRESS_LEVEL_PERMISSIBLE_VALUES))

      self.requestMaxCompressLevel = requestMaxCompressLevel


   def getExtensionString(self):
      """
      Returns the WebSocket extension configuration string as sent to the server.

      :returns: str -- PMCE configuration string.
      """
      pmceString = self.EXTENSION_NAME
      if self.acceptMaxCompressLevel:
         pmceString += "; c2s_max_compress_level"
      if self.requestMaxCompressLevel != 0:
         pmceString += "; s2c_max_compress_level=%d" % self.requestMaxCompressLevel
      return pmceString


   def __json__(self):
      """
      Returns a JSON serializable object representation.

      :returns: object -- JSON serializable represention.
      """
      return {'extension': self.EXTENSION_NAME,
              'acceptMaxCompressLevel': self.acceptMaxCompressLevel,
              'requestMaxCompressLevel': self.requestMaxCompressLevel}


   def __repr__(self):
      """
      Returns Python object representation that can be eval'ed to reconstruct the object.

      :returns: str -- Python string representation.
      """
      return "PerMessageBzip2Offer(acceptMaxCompressLevel = %s, requestMaxCompressLevel = %s)" % (self.acceptMaxCompressLevel, self.requestMaxCompressLevel)



class PerMessageBzip2Accept(PerMessageCompressAccept, PerMessageBzip2Mixin):
   """
   Set of parameters with which to accept an `permessage-bzip2` offer
   from a client by a server.
   """

   def __init__(self,
                offer,
                requestMaxCompressLevel = 0):
      """
      Constructor.

      :param offer: The offer being accepted.
      :type offer: Instance of :class:`autobahn.compress.PerMessageBzip2Offer`.
      :param requestMaxCompressLevel: Iff non-zero, server requests given "maximum compression level" - must be 1-9.
      :type requestMaxCompressLevel: int
      """
      if not isinstance(offer, PerMessageBzip2Offer):
         raise Exception("invalid type %s for offer" % type(offer))

      self.offer = offer

      if requestMaxCompressLevel != 0 and requestMaxCompressLevel not in self.COMPRESS_LEVEL_PERMISSIBLE_VALUES:
         raise Exception("invalid value %s for requestMaxCompressLevel - permissible values %s" % (requestMaxCompressLevel, self.COMPRESS_LEVEL_PERMISSIBLE_VALUES))

      if requestMaxCompressLevel != 0 and not offer.acceptMaxCompressLevel:
         raise Exception("invalid value %s for requestMaxCompressLevel - feature unsupported by client" % requestMaxCompressLevel)

      self.requestMaxCompressLevel = requestMaxCompressLevel


   def getExtensionString(self):
      """
      Returns the WebSocket extension configuration string as sent to the server.

      :returns: str -- PMCE configuration string.
      """
      pmceString = self.EXTENSION_NAME
      if self.offer.requestMaxCompressLevel != 0:
         pmceString += "; s2c_max_compress_level=%d" % self.offer.requestMaxCompressLevel
      if self.requestMaxCompressLevel != 0:
         pmceString += "; c2s_max_compress_level=%d" % self.requestMaxCompressLevel
      return pmceString


   def __json__(self):
      """
      Returns a JSON serializable object representation.

      :returns: object -- JSON serializable represention.
      """
      return {'extension': self.EXTENSION_NAME,
              'offer': self.offer.__json__(),
              'requestMaxCompressLevel': self.requestMaxCompressLevel}


   def __repr__(self):
      """
      Returns Python object representation that can be eval'ed to reconstruct the object.

      :returns: str -- Python string representation.
      """
      return "PerMessageBzip2Accept(offer = %s, requestMaxCompressLevel = %s)" % (self.offer.__repr__(), self.requestMaxCompressLevel,)



class PerMessageBzip2Response(PerMessageCompressResponse, PerMessageBzip2Mixin):
   """
   Set of parameters for `permessage-bzip2` responded by server.
   """

   @classmethod
   def parse(Klass, params):
      """
      Parses a WebSocket extension response for `permessage-bzip2` provided by a server to a client.

      :param params: Output from :method:`autobahn.websocket.WebSocketProtocol._parseExtensionsHeader`.
      :type params: list

      :returns: object -- A new instance of :class:`autobahn.compress.PerMessageBzip2Response`.
      """
      c2s_max_compress_level = 0
      s2c_max_compress_level = 0

      for p in params:

         if len(params[p]) > 1:
            raise Exception("multiple occurence of extension parameter '%s' for extension '%s'" % (p, Klass.EXTENSION_NAME))

         val = params[p][0]

         if p == 'c2s_max_compress_level':
            if val not in ['1', '2', '3', '4', '5', '6', '7', '8', '9']:
               raise Exception("illegal extension parameter value '%s' for parameter '%s' of extension '%s'" % (val, p, Klass.EXTENSION_NAME))
            else:
               c2s_max_compress_level = int(val)

         elif p == 's2c_max_compress_level':
            if val not in ['1', '2', '3', '4', '5', '6', '7', '8', '9']:
               raise Exception("illegal extension parameter value '%s' for parameter '%s' of extension '%s'" % (val, p, Klass.EXTENSION_NAME))
            else:
               s2c_max_compress_level = int(val)

         else:
            raise Exception("illegal extension parameter '%s' for extension '%s'" % (p, Klass.EXTENSION_NAME))

      response = Klass(c2s_max_compress_level, s2c_max_compress_level)
      return response


   def __init__(self,
                c2s_max_compress_level,
                s2c_max_compress_level):
      self.c2s_max_compress_level = c2s_max_compress_level
      self.s2c_max_compress_level = s2c_max_compress_level



class PerMessageBzip2(PerMessageCompress, PerMessageBzip2Mixin):
   """
   `permessage-bzip2` WebSocket extension processor.
   """
   DEFAULT_COMPRESS_LEVEL = 9

   @classmethod
   def createFromResponse(Klass, isServer, response):
      pmce = Klass(isServer,
                   response.s2c_max_compress_level,
                   response.c2s_max_compress_level)
      return pmce


   @classmethod
   def createFromAccept(Klass, isServer, accept):
      pmce = Klass(isServer,
                   accept.offer.requestMaxCompressLevel,
                   accept.requestMaxCompressLevel)
      return pmce


   def __init__(self,
                isServer,
                s2c_max_compress_level,
                c2s_max_compress_level):

      self._isServer = isServer
      self._compressor = None
      self._decompressor = None

      self.s2c_max_compress_level = s2c_max_compress_level if s2c_max_compress_level != 0 else self.DEFAULT_COMPRESS_LEVEL
      self.c2s_max_compress_level = c2s_max_compress_level if c2s_max_compress_level != 0 else self.DEFAULT_COMPRESS_LEVEL


   def __json__(self):
      return {'extension': self.EXTENSION_NAME,
              's2c_max_compress_level': self.s2c_max_compress_level,
              'c2s_max_compress_level': self.c2s_max_compress_level}


   def __repr__(self):
      return "PerMessageBzip2(isServer = %s, s2c_max_compress_level = %s, c2s_max_compress_level = %s)" % (self._isServer, self.s2c_max_compress_level, self.c2s_max_compress_level)


   def startCompressMessage(self):
      if self._isServer:
         if self._compressor is None:
            self._compressor = bz2.BZ2Compressor(self.s2c_max_compress_level)
      else:
         if self._compressor is None:
            self._compressor = bz2.BZ2Compressor(self.c2s_max_compress_level)


   def compressMessageData(self, data):
      return self._compressor.compress(data)


   def endCompressMessage(self):
      data = self._compressor.flush()

      ## there seems to be no "flush without close stream", and after
      ## full flush, compressor must not be reused
      self._compressor = None

      return data


   def startDecompressMessage(self):
      if self._decompressor is None:
         self._decompressor = bz2.BZ2Decompressor()


   def decompressMessageData(self, data):
      return self._decompressor.decompress(data)


   def endDecompressMessage(self):
      self._decompressor = None