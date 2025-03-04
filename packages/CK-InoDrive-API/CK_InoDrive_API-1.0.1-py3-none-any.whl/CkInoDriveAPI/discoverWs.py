import logging

from .defines import CK
from .utils import Utils


class DiscoverWs(object):
    def __init__(self, **kwargs):
        self._get_connection_handle = kwargs.get('getConnectionHandle')

    @property
    def _connection_handle(self):
        return self._get_connection_handle()

    def dispose(self):
        return

    def get_info(self):
        try:
            # Send request and wait for response
            resp = self._connection_handle.request(Utils.get_tlv(CK.SPECIAL.GET_DISCOVER_INFO))

            if resp.get('error'):
                logging.error(f"Retrieving discover info failed...")
                return None

            result = None

            resp_items = resp.get('items')
            if resp_items and len(resp_items) > 0:
                data = resp_items[0].get('data')
                result = Utils.decode_discover_data(data)

            if result is None:
                logging.exception("Message decoding error")
                return None

            return result
        except Exception as ex:
            logging.exception(ex)

        return None
