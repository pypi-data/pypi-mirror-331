"""Allows for Single-Sign On HTTP Negotiate authentication using the niquests library on Windows."""

import niquests
import urllib3_future

from .niquests_negotiate_sspi import HttpNegotiateAuth

__all__ = ["HttpNegotiateAuth"]

# Monkeypatch urllib3 to expose the peer certificate
http_response = urllib3_future.response.HTTPResponse
orig_http_response__init__ = http_response.__init__

http_adapter = niquests.adapters.HTTPAdapter
orig_http_adapter_build_response = http_adapter.build_response


def new_http_response__init__(self, *args, **kwargs):
    orig_http_response__init__(self, *args, **kwargs)
    try:
        self.peercert = self._connection.sock.getpeercert(binary_form=True)
    except AttributeError:
        self.peercert = None


def new_http_adapter_build_response(self, request, resp):
    response = orig_http_adapter_build_response(self, request, resp)
    try:
        response.peercert = resp.peercert
    except AttributeError:
        response.peercert = None
    return response


http_response.__init__ = new_http_response__init__
http_adapter.build_response = new_http_adapter_build_response
