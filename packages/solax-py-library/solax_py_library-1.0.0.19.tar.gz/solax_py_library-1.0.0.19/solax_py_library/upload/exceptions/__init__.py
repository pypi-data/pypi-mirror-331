from solax_py_library.exception import SolaxBaseError
from .upload_error import ConfigurationError, ConnectError, LoginError, SendDataError

__all__ = [
    "SolaxBaseError",
    "ConnectError",
    "LoginError",
    "SendDataError",
    "ConfigurationError",
]
