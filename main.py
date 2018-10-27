#! venvs/bin/python

from cal_client import c_client
from trello_client import t_client
from trello import exceptions
import sys
import uuid
from config import config
import logging

logging.basicConfig(filename='trello_cal.log', filemode='w', level=logging.DEBUG, format='[%(asctime)s]%(levelname)s: %(message)s', datefmt='%H:%M:%S')

def personal_done_calendarise():
    all_cards_in_done = t_client.get_list_cards(
        t_client.get_board_id('personal'),
        t_client.get_list_id('personal','done'))
    logging.info("got cards!")
    session_id = uuid.uuid1().int
    for card in all_cards_in_done:
        if t_client.is_new_card(card):
            c_client.event_to_cal(card)
            t_client.log_card(card, session_id)
            t_client.archive_card(card)


def work_done_calendarise():
    all_cards_in_done = t_client.get_list_cards(work_board_id, work_board_done_list_id, [my_id])
    session_id = uuid.uuid1().int
    for card in all_cards_in_done:
        if t_client.is_new_card(card):
            c_client.event_to_cal(card)
            t_client.log_card(card, session_id)

def set_config(file=None):
    if file == None:
        try:
            file = sys.argv[1]
        except IndexError:
            file = "config/config.yml"
    logging.info("using file: %s", file)
    config.init(file)
    logging.info("config successfully loaded: %s" % config.config)

def main():
    try:
        logging.info("Routine: %s", sys.argv[-1])
        if sys.argv[-1] == "personal":
            personal_done_calendarise()
        if sys.argv[-1] == "work":
            work_done_calendarise()
        if sys.argv[-1] == "all":
            personal_done_calendarise()
            work_done_calendarise()
        else:
            personal_done_calendarise()
    except (exceptions.Unauthorized):
        logging.warn("Not logged in yet!")
        t_client.login()
        main()
    except exceptions.ResourceUnavailable:
        # TODO: suggest changing it
        logging.warn("ResourceUnavailable: This may mean your board or list ID may have changed")


if __name__ == '__main__':
    set_config()
    t_client.init()
    c_client.init()
    main()

# login()
# personal_done_calendarise()
# work_done_calendarise()
