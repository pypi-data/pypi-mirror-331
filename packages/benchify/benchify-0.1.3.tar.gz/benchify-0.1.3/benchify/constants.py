from enum import Enum

CONFIG_DIR_PATH = '.benchify'
TAR_FILE_PATH = 'benchify.tar'

AUTH_URL = "https://app.benchify.com/api/cli?"
API_URL_GET_METADATA = "https://api.benchify.com/cli/get-metadata"
API_URL_CONFIG = "https://api.benchify.com/cli/config?"

class Command(Enum):
    LOGIN = "login"
    LOGOUT = "logout"
    INIT = "init"
    TEST = "test"

class HTTPMethod(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
