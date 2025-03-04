import logging
import weakref
from ._version import get_version_number
from .callback import Callback

from .wsHandle import InoDriveWS
from .file import File
from .discoverWs import DiscoverWs
from .IO import IO
from .userApp import UserApp
from .sysControl import SysControl


class InoDrive(object):
    version = None
    _kwargs = None
    _connection_handle_instance = None

    def __init__(self, **kwargs):
        self.version = get_version_number()
        self._kwargs = kwargs
        logging.debug('Create InoDrive instance...')
        self._auto_connect = kwargs.get('autoConnect', False)

        # Callbacks
        self._callback = Callback()

        if 'callbacks' in self._kwargs:
            if type(self._kwargs['callbacks']) is dict:
                for name, functions in self._kwargs['callbacks'].items():
                    if type(functions) is not list:
                        functions = [functions]
                    for func in functions:
                        if callable(func):
                            self._callback.on(name, func)

        # ==============================================================================================================
        # MODULES BEGIN
        # ==============================================================================================================
        self.File = File(**kwargs, getConnectionHandle=self._get_connection_handle, callback=self._callback)
        self.Discover = DiscoverWs(**kwargs, getConnectionHandle=self._get_connection_handle, callback=self._callback)
        self.IO = IO(**kwargs, getConnectionHandle=self._get_connection_handle, callback=self._callback)
        self.UserApp = UserApp(**kwargs, getConnectionHandle=self._get_connection_handle, callback=self._callback)
        self.SysControl = SysControl(**kwargs, getConnectionHandle=self._get_connection_handle, callback=self._callback)
        # ==============================================================================================================
        # MODULES END
        # ==============================================================================================================

        # ==============================================================================================================
        # CONNECTION
        # ==============================================================================================================
        if "useFallback" in self._kwargs:
            self._use_fallback = False if self._kwargs["useFallback"] == False else True
        else:
            self._use_fallback = True

        if "secureConnection" in self._kwargs:
            self._secure_connection = False if self._kwargs["secureConnection"] == False else True
        else:
            self._secure_connection = True

        if self._auto_connect:
            self.connect()
        # ==============================================================================================================
        # CONNECTION END
        # ==============================================================================================================

        # Finalizer weak reference to ensure InoDrive Object is cleaned up on code exit
        self._finalizer = weakref.finalize(self, self.dispose)

    def __del__(self):
        self._finalizer()

    @property
    def callback(self):
        return self._callback

    @property
    def on(self):
        return self._callback.on

    def dispose(self):
        try:
            if self.UserApp:
                self.UserApp.dispose()

            if self._connection_handle_instance is not None:
                self._connection_handle_instance = self._connection_handle_instance.dispose()
        except Exception as ex:
            logging.exception(ex)

    def connect(self):
        try:
            if self._connection_handle_instance is None:
                # Connection handle is not created yet
                connection_handle = None
                if self._secure_connection:
                    try:
                        connection_handle = InoDriveWS(
                            **self._kwargs,
                            callback=self._callback,
                            secure=True
                        )
                        self._connection_handle_instance = connection_handle
                        connection_handle.connect()
                    except Exception as ex:
                        logging.exception(ex)
                        if connection_handle:
                            connection_handle = connection_handle.dispose()

                        if not self._use_fallback:
                            return
                else:
                    connection_handle = InoDriveWS(**self._kwargs, callback=self._callback, secure=False)
                    self._connection_handle_instance = connection_handle
                    connection_handle.connect()
            else:
                self._connection_handle_instance.connect()
        except Exception as ex:
            logging.exception(ex)

    def disconnect(self):
        try:
            if self._connection_handle_instance is not None:
                self._connection_handle_instance.disconnect()
        except Exception as ex:
            logging.exception(ex)

    def set_target(self, target=None):
        if type(target) is not str:
            return

        if self._connection_handle_instance is not None:
            return self._connection_handle_instance.set_target(target)

        self._kwargs.host = target

    @property
    def connected(self):
        if self._connection_handle_instance is not None:
            return self._connection_handle_instance.connected

        return False

    def _get_connection_handle(self):
        if self._connection_handle_instance is not None:
            return self._connection_handle_instance
