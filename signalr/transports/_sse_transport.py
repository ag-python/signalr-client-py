import json
import sseclient
from ._transport import Transport


class ServerSentEventsTransport(Transport):
    def __init__(self, session, event_handlers):
        Transport.__init__(self, session, event_handlers)
        self.__response = None

    def _get_name(self):
        return 'serverSentEvents'

    def start(self, connection):
        connect_url = self._get_url(connection, 'connect')
        self.__response = \
            iter(sseclient.SSEClient(connect_url, session=self._session))
        self._session.get(self._get_url(connection, 'start'))

        def _receive():
            try:
                notification = next(self.__response)
            except StopIteration:
                return
            else:
                if notification.data != 'initialized':
                    self._handle_notification(notification.data)

        return _receive

    def send(self, connection, data):
        self._session.post(self._get_url(connection, 'send'), data={'data': json.dumps(data)})

    def close(self, connection):
        self._session.get(self._get_url(connection, 'abort'))
