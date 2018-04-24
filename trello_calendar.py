from cal_client import event_to_cal, hour
from trello_client import *
from trello import util
import os
import sys


# with open('config.yml') as c:
#     config = yaml.load(c)
# trello_config = config['TRELLO']
file = open("config.yml","r")
yaml = YAML()
config = yaml.load(file)

os.environ['TRELLO_API_KEY'] = trello_config['api_key']
print(os.environ['TRELLO_API_KEY'])
os.environ['TRELLO_API_SECRET'] = trello_config['api_secret']
print(os.environ['TRELLO_API_SECRET'])

def login():
    api_key = trello_config['api_key']
    api_secret = trello_config['api_secret']
    # client = TrelloClient(api_key, api_secret)
    # out = util.create_oauth_token()
    config['TRELLO']['oauth_token'] = "it works" # out.oauth_token
    config['TRELLO']['oauth_token_secret'] = "yes it does" # out.oauth_token_secret
    file_w = open("config.yml", "w")
    yaml.dump(config, file_w)
    file_w.close()
    # print("outputi: %s == %s" % out.oauth_token_secret, trello_config['oauth_token_secret'] )

def personal_done_calendarise():
    all_cards_in_done = get_list_cards(personal_board_id, personal_board_done_list_id)
    session_id = uuid.uuid1().int
    print(all_cards_in_done.length())
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

# if sys.argv[1] == "personal":
#     personal_done_calendarise()
# if sys.argv[1] == "work":
#     work_done_calendarise()
# if sys.argv[1] == "all":
#     personal_done_calendarise()
#     work_done_calendarise()

login()

# login()
# personal_done_calendarise()
# work_done_calendarise()
