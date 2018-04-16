from cal_client import make_event, hour
from trello_client import *

def checklist_print(checklists):
    checklist_out = ""
    for checklist in checklists:
        checklist_out += "\nCHECKLIST: " + checklist.name +"\n"
        for item in checklist.items:
            checklist_out += "- " + item['name'] + "\n"
    return checklist_out



def pretty_print(card):
    print("Title: %s:\nDescription: %s\n%s\nFinished at:%s\n\n" % (
        card.name,
        card.description,
        checklist_print(card.fetch_checklists()),
        card.listCardMove_date()[0][-1]))

def personal_done_calendarise():
    all_cards_in_done = client.get_board(personal_board_id).get_list(
        personal_board_done_list_id).list_cards()
    for card in all_cards_in_done:
        name = card.name
        description = card.description + "\n"  + checklist_print(card.fetch_checklists())
        end = card.listCardMove_date()[0][-1]
        pretty_print(card)
        make_event(end,hour,name,description)
        card.set_closed(True)

def work_done_calendarise():
    all_cards_in_done = client.get_board(work_board_id).get_list(
        work_board_done_list_id).list_cards()
    pretty_print(all_cards_in_done[2])
    # for card in all_cards_in_done:
    #     name = card.name
    #     description = card.description
    #     end = card.listCardMove_date()[0][-1]
    #     pretty_print(card)

work_done_calendarise()
