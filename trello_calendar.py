from datetime import datetime, timedelta
from cal_client import make_event, hour
from trello_client import *


all_cards_in_done = client.get_board(personal_board_id).get_list(personal_board_done_list_id).list_cards()

for card in all_cards_in_done:
    name = card.name
    description = card.description
    end = card.listCardMove_date()[0][-1]
    print("Title: %s:\nDescription: %s\nFinished at:%s\n\n" % (name, description,end))
    make_event(end,hour,name,description)
    card.set_closed(True)
