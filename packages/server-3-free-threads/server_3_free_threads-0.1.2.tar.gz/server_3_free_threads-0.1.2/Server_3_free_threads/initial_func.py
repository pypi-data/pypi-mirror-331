import logging
import dotenv
from threading import Thread
import os
import load_app
import parser_args
import server_actions
# from Server_3_free_threads.load_app import load_app as l_app
# from Server_3_free_threads.parser_args import ParserCommandLineArgs as p_args
import importlib
# from Server_3_free_threads.server_actions import ServerActions


def main():
    dotenv.load_dotenv()
    logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(filename)s:%(funcName)s] %(message)s')
    log = logging.getLogger(__name__)

    host = os.getenv("HOST")
    port_default = int(os.getenv("PORT"))
    connection_queue = int(os.getenv("CONNECTION_QUEUE"))

    module = None
    pars_args = parser_args.ParserCommandLineArgs(port_default)
    pars_args.find_args()
    port, path_app = pars_args.port, pars_args.app
    if path_app:
        if load_app.load_app(path_app):
            module = importlib.import_module(path_app)
            importlib.invalidate_caches()
    else:
        log.info("относительный путь к приложению не указан, сервер запущен в тестовом режиме")
    serv_act = server_actions.ServerActions(host=host, port=port, connection_queue=connection_queue)
    threads = (Thread(target=serv_act.accepting_connections),
               Thread(target=serv_act.reading_from_socket),
               Thread(target=serv_act.sending_to_socket, args=(module, )),
               Thread(target=serv_act.close_client_sock),)

    for elem in threads:
        elem.start()
    for elem in threads:
        elem.join()
