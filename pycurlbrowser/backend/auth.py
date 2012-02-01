# coding: utf-8

"""
Authentication methods.
"""

class Auth(object):

    """
    Base auth class.
    """

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __ne_(self, other):
        return not self.__eq__(other)

class BasicAuth(Auth):

    """
    Basic HTTP authentication.
    """

class DigestAuth(Auth):

    """
    HTTP Digest authentication.
    """

class OpenAuth(Auth):

    """
    OAuth.
    """

    def __init__(self, access_token, access_token_secret, consumer_key, consumer_secret, header_auth):
        self.access_token        = access_token
        self.access_token_secret = access_token_secret
        self.consumer_key        = consumer_key
        self.consumer_secret     = consumer_secret
        self.header_auth         = header_auth
