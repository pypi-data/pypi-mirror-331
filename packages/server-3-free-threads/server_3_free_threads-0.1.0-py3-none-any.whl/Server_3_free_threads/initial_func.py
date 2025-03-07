import logging
import dotenv
from threading import Thread
import os
from utills.load_app import load_app as l_app
from utills.parser_args import ParserCommandLineArgs as p_args
import importlib
from server_actions import ServerActions


def main():
    dotenv.load_dotenv()
    logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(filename)s:%(funcName)s] %(message)s')
    log = logging.getLogger(__name__)

    host = os.getenv("HOST")
    port_default = int(os.getenv("PORT"))
    connection_queue = int(os.getenv("CONNECTION_QUEUE"))

    module = None
    parser_args = p_args(port_default)
    parser_args.find_args()
    port, path_app = parser_args.port, parser_args.app
    if path_app:
        if l_app(path_app):
            module = importlib.import_module(path_app)
            importlib.invalidate_caches()
    else:
        log.info("относительный путь к приложению не указан, сервер запущен в тестовом режиме")
    server_actions = ServerActions(host=host, port=port, connection_queue=connection_queue)
    threads = (Thread(target=server_actions.accepting_connections),
               Thread(target=server_actions.reading_from_socket),
               Thread(target=server_actions.sending_to_socket, args=(module, )),
               Thread(target=server_actions.close_client_sock),)

    for elem in threads:
        elem.start()
    for elem in threads:
        elem.join()
