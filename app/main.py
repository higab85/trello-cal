#! venvs/bin/python
import os
import sys
sys.path.insert(
        0, 
        os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.cal_client import C_CLIENT
from app.trello_client import T_CLIENT
from trello import exceptions
import sys
import uuid
from app.config import CONFIG
import logging

logging.basicConfig(
    filename='trello_cal.log',
    filemode='w',
    level=logging.DEBUG,
    format='[%(asctime)s]%(levelname)s: %(message)s',
    datefmt='%H:%M:%S')

def default_board_calendarise():
    logging.info("default_board_calendarise")

    board_id = T_CLIENT.get_board_id('default')
    list_id = T_CLIENT.get_list_id('default', 'done')
    all_cards_in_done = T_CLIENT.get_list_cards(board_id, list_id)
    logging.info("got cards!")
    session_id = uuid.uuid1().int
    for card in all_cards_in_done:
        if T_CLIENT.is_new_card(card):
            C_CLIENT.event_to_cal(card)
            T_CLIENT.log_card(card, session_id)
            T_CLIENT.archive_card(card)


def set_config():
    try:
        file = sys.argv[1]
    except IndexError:
        file = "config/config.yml"
    logging.info("using file: %s", file)
    CONFIG.init(cfile=file)
    logging.info("config successfully loaded: %s", CONFIG.config)

def main():
    try:
        default_board_calendarise()
    except exceptions.Unauthorized:
        logging.warning("Not logged in yet!")
        T_CLIENT.login()
        main()
    except exceptions.ResourceUnavailable:
        logging.warning("ResourceUnavailable: \
                This may mean your board or list ID may have changed")
        main()


if __name__ == '__main__':
    set_config()
    T_CLIENT.init()
    C_CLIENT.init()
    main()

# login()
# personal_done_calendarise()
# work_done_calendarise()
