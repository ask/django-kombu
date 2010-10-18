from Queue import Empty

from anyjson import serialize, deserialize
from kombu.transport import virtual

from django.core import exceptions as errors

from djkombu.models import Queue


class Channel(virtual.Channel):

    def _new_queue(self, queue, **kwargs):
        Queue.objects.get_or_create(name=queue)

    def _put(self, queue, message, **kwargs):
        Queue.objects.publish(queue, serialize(message))

    def _get(self, queue):
        self.refresh_connection()
        m = Queue.objects.fetch(queue)
        if m:
            return deserialize(m)
        raise Empty()

    def _size(self, queue):
        return Queue.objects.size(queue)

    def _purge(self, queue):
        return Queue.objects.purge(queue)

    def refresh_connection(self):
        from django.db import connection
        connection.close()


class DatabaseTransport(virtual.Transport):
    Channel = Channel

    default_port = 0
    connection_errors = ()
    channel_errors = (errors.ObjectDoesNotExist,
                      errors.MultipleObjectsReturned)
