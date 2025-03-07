import threading
import time
from collections import deque
import socket
import logging
import sys
import select
import os
import response_headers


logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(filename)s:%(funcName)s] %(message)s')
log = logging.getLogger(__name__)


class ServerActions:

    def __init__(self, host, port, connection_queue):
        self._host = host
        self._port = port
        self._connection_queue = connection_queue
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._epoll_object_for_read = select.epoll()
        self._deque_object_for_write = deque()
        self._connections_dict = {}
        self._all_client_sockets = []
        self._write_in_sock_event = threading.Event()
        self._close_client_sock_event = threading.Event()
        self._response_cap = self._response_cap_method()

    def _preparation_for_accept(self):
        self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server_socket.bind((self._host, self._port))
        self._server_socket.listen(self._connection_queue)
        log.info("server listen, HOST: %s, PORT: %s", self._host, self._port)
        try:
            log.info(f'GIL enabled: {sys._is_gil_enabled()}')
        except AttributeError:
            pass

    def accepting_connections(self) -> None:
        """
        it's first step
        next step: reading_from_socket
        :return:
        """
        self._preparation_for_accept()
        with self._server_socket as sock:
            while True:
                conn, addr = sock.accept()
                conn.setblocking(False)
                fd = conn.fileno()
                self._connections_dict[str(fd)] = conn
                self._epoll_object_for_read.register(
                    fd=fd, eventmask=select.EPOLLIN | select.EPOLLET
                )

    @staticmethod
    def _recv_from_sock(sock: socket) -> bytes:
        total_data = b''
        data = None
        while True:
            try:
                data = sock.recv(2048)
            except BlockingIOError:
                return total_data
            else:
                if data:
                    total_data += data
                else:
                    return total_data

    def reading_from_socket(self) -> None:
        """
        next step: sending_to_socket
        :return:
        """
        while True:
            fd_set = self._epoll_object_for_read.poll()
            for fd, event in fd_set:
                self._epoll_object_for_read.unregister(fd)
                sock = self._connections_dict.pop(str(fd))
                data = self._recv_from_sock(sock)
                if data:
                    data = data.decode()
                    self._deque_object_for_write.append((sock, data))
                    self._write_in_sock_event.set()
                else:
                    sock.close()

    def sending_to_socket(self, module) -> None:
        app_django = None
        environ = dict(os.environ.items())
        environ['wsgi.input'] = sys.stdin
        environ['wsgi.errors'] = sys.stderr
        environ['wsgi.url_scheme'] = 'http'
        environ['wsgi.version'] = (1, 0)
        environ['wsgi.multithread'] = True
        environ['wsgi.multiprocess'] = False
        environ['wsgi.run_once'] = False
        environ['SERVER_PORT'] = self._port
        environ['SERVER_NAME'] = 'localhost'
        if module:
            app_django = module.application
        while True:
            self._write_in_sock_event.wait()
            self._clear_deque_for_write(app_django, environ)
            self._write_in_sock_event.clear()

    def _clear_deque_for_write(self, app_django, environ):
        sock, data = self._deque_object_for_write.popleft()
        data = data.splitlines()[0]
        method, path, _ = data.split(' ')
        environ['PATH_INFO'] = path
        environ['REQUEST_METHOD'] = method
        if app_django:
            rh = response_headers.ResponseHeaders()
            result = app_django(environ, rh.start_response)
            for r in result:
                response = rh.headers + r
                sock.sendall(response)
        else:
            sock.sendall(self._response_cap)
        self._all_client_sockets.append(sock)
        self._close_client_sock_event.set()

    @staticmethod
    def _response_cap_method():
        response = (f'HTTP/1.1 200 OK\r\n'
                    f'Content-Type: text/html\r\n'
                    f'Connection: close\r\n\r\n'
                    '<h1 style="display: flex; justify-content: center; font-style: italic;">Test page</h1>\n')
        return response.encode()

    def close_client_sock(self):
        while True:
            self._close_client_sock_event.wait()
            time.sleep(0.3)
            for sock in self._all_client_sockets:
                sock.close()
            self._close_client_sock_event.clear()
