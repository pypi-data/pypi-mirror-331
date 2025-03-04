import logging


class Callback(object):
    _context = None
    _callbacks = {}

    def __init__(self, **kwargs):
        self._context = kwargs.get('context', self)

    def on(self, name=None, func=None):
        try:
            callbacks = {}

            if type(name) is dict:
                callbacks = name
            elif type(name) is str and callable(func):
                callbacks[name] = func
            else:
                return

            for callback_name, callback_function in callbacks.items():
                if type(callback_name) is not str:
                    continue

                if not callable(callback_function):
                    continue

                if callback_name not in self._callbacks:
                    # Callback does not exist
                    self._callbacks[callback_name] = [callback_function]
                    continue

                if callback_function not in self._callbacks[callback_name]:
                    # Function is not in callback group
                    self._callbacks[callback_name].append(callback_function)
                    continue

        except Exception as ex:
            logging.exception(ex)

    def remove(self, name=None, func=None):
        try:
            if type(name) is not str:
                return

            if not callable(func):
                return

            if self._callbacks[name] and func in self._callbacks[name]:
                # Function exist so we need to remove it - removing callback.
                self._callbacks[name].pop(self._callbacks[name].index(func))

            if len(self._callbacks[name]) == 0:
                # There are no more functions in the group - remove the group
                del self._callbacks[name]

        except Exception as ex:
            logging.exception(ex)

    def dispatch(self, callback_name=None, *args):
        try:
            # Get call back group
            if callback_name in self._callbacks:
                callbacks = self._callbacks[callback_name]
                if callbacks is not None:
                    for callback in callbacks:
                        # Call each callback
                        if callable(callback):
                            callback(*args)

        except Exception as ex:
            logging.exception(ex)

    def dispatch_with_context(self, context=None, callback_name=None, *args):
        try:
            # Get call back group
            if callback_name in self._callbacks:
                callbacks = self._callbacks[callback_name]
                if callbacks is not None:
                    for callback in callbacks:
                        # Call each callback
                        if callable(callback):
                            callback(context, *args)

        except Exception as ex:
            logging.exception(ex)
