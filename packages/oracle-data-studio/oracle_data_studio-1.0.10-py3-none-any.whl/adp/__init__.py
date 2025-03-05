'''
    Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl/.

    Copyright (c) 2023-2025, Oracle and/or its affiliates.

    ORDS API Python Client
'''


from .rest import Rest
from .db_util import DbUtils
from .adp_analytics import AdpAnalytics
from .adp_ingest import AdpIngest
from .adp_insight import AdpInsight
from .adp_misc import AdpMisc

from .adp import Adp

__version__ = "1.0.23"

def login(url : str, username : str, password : str) -> Adp:
    ''' Login to the ORDS
    
        @param url (String) - url for ORDS with protocol, host and port
        Another parameters:
        @param username (String) - name of the schema
        @param password  (String) - password of the schema
    '''

    rest = Rest()
    rest.login(url, username, password)
    ords = Adp(rest)
    return ords


def connect(url: str = None) -> Adp:
    ''' Login to the ORDS using database cursor. This function does not require url, username, and password.
        Url and username are taken from sql queries, client Id and client secret are generated when they does not exist.
        Login is performing using OAuth access token     
    '''

    #pylint: disable=C0415
    try:
        import oml
        cursor=oml.cursor()
        db_utils = DbUtils()
        db_utils.set_cursor(cursor)
        if url is None:
            url = db_utils.get_url()
        username = db_utils.get_username()

        client = db_utils.get_client()

        rest = Rest()
        rest.connect(url, username, client)
        ords = Adp(rest)
        return ords

    except ImportError as exp:
        raise ImportError("OML is not defined") from exp
