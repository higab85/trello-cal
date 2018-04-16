from cal_client import make_event, hour
from trello_client import *

def get_list_cards(board, list):
    return client.get_board(board).get_list(list).list_cards()

def personal_done_calendarise():
    all_cards_in_done = get_list_cards(personal_board_id, personal_board_done_list_id)
    for card in all_cards_in_done:
        make_event(card)
        card.set_closed(True)

def work_done_calendarise():
    all_cards_in_done = get_list_cards(work_board_id, work_board_done_list_id)
    pretty_print(all_cards_in_done[2])

personal_done_calendarise()
