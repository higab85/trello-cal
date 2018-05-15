from cal_client import event_to_cal, hour
from trello_client import *
from trello import exceptions
import os
import sys
from pprint import pprint


def personal_done_calendarise():
    all_cards_in_done = get_list_cards(
        get_board_id('personal'),
        get_list_id('personal','done'))
    session_id = uuid.uuid1().int
    for card in all_cards_in_done:
        if is_new_card(card):
            event_to_cal(card)
            log_card(card, session_id)
            archive_card(card)

def work_done_calendarise():
    all_cards_in_done = get_list_cards(work_board_id, work_board_done_list_id, [my_id])
    session_id = uuid.uuid1().int
    for card in all_cards_in_done:
        if is_new_card(card):
            event_to_cal(card)
            log_card(card, session_id)

try:
    if sys.argv[1] == "personal":
        personal_done_calendarise()
    if sys.argv[1] == "work":
        work_done_calendarise()
    if sys.argv[1] == "all":
        personal_done_calendarise()
        work_done_calendarise()
except exceptions.Unauthorized:
    print("Not logged in yet!")
    login()
except IndexError:
    print("No option given!")
    print("trello_cal personal # for personal trello \
            \ntrello_cal work # for work board \
            \ntrello_cal all # for both")
    pass


# login()
# personal_done_calendarise()
# work_done_calendarise()
