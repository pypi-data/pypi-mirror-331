import sys
import logging
import re

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(filename)s:%(funcName)s] %(message)s')
log = logging.getLogger(__name__)


class ParserCommandLineArgs:

    def __init__(self, port):
        self._port = port
        self._app = None
        self.port_re = re.compile(r'port=(?P<port>\d{0,4})')
        self.app_re = re.compile(r'app=(?P<app>.+)')
        self.all_param = sys.argv[1:]

    @property
    def port(self):
        return self._port

    @property
    def app(self):
        return self._app

    def find_args(self):
        if not self.all_param:
            log.info("параметры не указаны в командной строке, использованы значения по умолчанию")
        for param in self.all_param:
            result_port = self.pars_port(param)
            result_app = self.pars_path(param)

            if result_port:
                self._port = result_port

            if result_app:
                self._app = result_app

    def pars_port(self, param):
        result_port = self.port_re.match(param)
        if result_port:
            port = int(result_port.group('port'))
            return port

    def pars_path(self, param):
        result_app = self.app_re.match(param)
        if result_app:
            app = result_app.group('app')
            return app
