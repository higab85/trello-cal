from trello import TrelloClient, util
from ruamel.yaml import YAML
from peewee import *
from datetime import date,datetime
import hashlib
import uuid
from pprint import pprint

db = SqliteDatabase('sent_to_cal.db')

file = open("config.yml","r")
yaml = YAML()
config = yaml.load(file)

# with open('config.yml') as c:
#     config = yaml.load(c)
trello_config = config['TRELLO']
boards = trello_config['boards']


# TODO: !!
# def write_to_yaml(position, value):
#     file = open("config.yml","r")
#     yaml = YAML()
#     config = yaml.load(file)
#     for category in position:
        # config = config[category]

def login():
    api_key = trello_config['api_key']
    api_secret = trello_config['api_secret']
    client = TrelloClient(api_key, api_secret)
    out = util.create_oauth_token(key=api_key, secret=api_secret)
    config['TRELLO']['oauth_token'] = out['oauth_token']
    config['TRELLO']['oauth_token_secret'] = out['oauth_token_secret']
    file_w = open("config.yml", "w")
    yaml.dump(config, file_w)
    file_w.close()

client = TrelloClient(
    api_key=trello_config['api_key'],
    api_secret=trello_config['api_secret'],
    token=trello_config['oauth_token'],
    token_secret=trello_config['oauth_token_secret'])


class LoggedCard(Model):
    card_id = CharField()
    card_hash = CharField()
    datetime_added = DateField()
    session_id = CharField()

    def __string__(self):
        return (
            card_id,"\n",
            card_hash,"\n",
            datetime_added,"\n",
            session_id)

    class Meta:
        database = db

def archive_card(card):
    card.set_closed(True)

def get_checklists(card):
    checklists = card.fetch_checklists()
    checklist_out = ""
    for checklist in checklists:
        checklist_out += "\nCHECKLIST: " + checklist.name +"\n"
        for item in checklist.items:
            checklist_out += "- " + item['name'] + "\n"
    return checklist_out

def get_description(card):
    return card.description + "\n" + get_checklists(card)


def pretty_print(card):
    print("Title: %s:\nDescription:%s\nFinished at:%s\n\n" % (
        card.name,
        get_description(card),
        card.listCardMove_date()[0][-1]))

def card_hash(card):
    hashable = get_description(card)
    return hashlib.sha256(hashable.encode()).hexdigest()

def log_card(card, session):
    event = LoggedCard.create(
        card_id = card.id,
        card_hash = card_hash(card),
        datetime_added = datetime.now(),
        session_id = session)

def is_new_card(card):
    try:
        LoggedCard.get(LoggedCard.card_id == card.id)
    except DoesNotExist:
        print("New card:", card.name)
        return True
    return False

def get_list_cards(board_id, list_id, members=[]):
    print("Getting list %s from board %s with members %s" % (list_id, board_id, members))
    cards = client.get_board(board_id).get_list(list_id).list_cards()
    return filter(lambda x: x.member_id == members, cards)

def board_to_yaml(name, board_id):
    trello_config['boards'][name]['id'] = board_id
    file_w = open("config.yml", "w")
    yaml.dump(config, file_w)
    file_w.close()
    print("written")

def find_board_id(board_name):
    print("You don't seem to have a %s board! \n\
Please select one of the following: " % board_name)
    for id,board in enumerate(client.list_boards()):
        print("%s:%s" % (id, board))
    board_num = int(input("What is the id of your %s board?" % (board_name)))
    board_id = client.list_boards()[board_num].id
    board_to_yaml(board_name, board_id)
    return board_id

def get_board_id(board_name):
    if boards[board_name]['id'] == None:
        return find_board_id(board_name)
    else:
        return boards[board_name]['id']

def list_to_yaml(board_name, list_name, list_id):
    trello_config['boards'][board_name][list_name] = list_id
    file_w = open("config.yml", "w")
    yaml.dump(config, file_w)
    file_w.close()
    print("%s id has been written to config" % list_name)

def find_list_id(board_config, list_name):
    print("You don't seem to have a %s list, on your this board! \n\
Please select one of the following: " % list_name)
    board_id = str(board_config['id'])
    board_name = board_config['name']
    for id,list in enumerate(client.get_board(board_id).open_lists()):
        print("%s:%s" % (id, list))
    list_num = int(input("What is the id of your %s list?" % (list_name)))
    list_id = client.get_board(board_id).open_lists()[list_num].id
    list_to_yaml(board_name, list_name, list_id)
    return list_id

def get_list_id(board_name, list_name):
    board_config = boards[board_name]
    if board_config[list_name] == None:
        return find_list_id(board_config, list_name)
    else:
        return boards[board_name][list_name]


## Get a board ID like so:
# 1. client.list_boards()
# 2. client.list_boards()[number of board].id
# [3.(for list id) print(client.get_board(work_board_id).open_lists()[3].id) ]


# personal_board = boards['personal']
#
# if (personal_board == None):
#     find_board('personal')
#
# personal_board_id  = boards['personal']['id']
# personal_board_done_list_id = boards['personal']['done']
#
# work_board_id  = boards['work']['id']
# work_board_done_list_id = boards['work']['done']
#
# my_id = boards['work']['member_id']

# for member in client.get_board(work_board_id).all_members():
#     print("Name: %s, ID: %s\n" % (member.full_name, member.id))
