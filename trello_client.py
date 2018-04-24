from trello import TrelloClient
from ruamel.yaml import YAML
from peewee import *
from datetime import date,datetime
import hashlib
import uuid


db = SqliteDatabase('sent_to_cal.db')

file = open("config.yml","r")
yaml = YAML()
config = yaml.load(file)

# with open('config.yml') as c:
#     config = yaml.load(c)
trello_config = config['TRELLO']

def login():
    api_key = trello_config['api_key']
    api_secret = trello_config['api_secret']
    client = TrelloClient(api_key, api_secret)
    out = util.create_oauth_token()
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

client = TrelloClient(
    api_key=trello_config['api_key'],
    api_secret=trello_config['api_secret'])

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

def get_list_cards(board, list, members=[]):
    cards = client.get_board(board).get_list(list).list_cards()
    return filter(lambda x: x.member_id == members, cards)

## Get a board ID like so:
# 1. client.list_boards()
# 2. client.listboards()[number of board].id
# [3.(for list id) print(client.get_board(work_board_id).open_lists()[3].id) ]
boards = trello_config['boards']

personal_board_id  = boards['personal']['id']
personal_board_done_list_id = boards['personal']['lists']['done']

work_board_id  = boards['work']['id']
work_board_done_list_id = boards['work']['lists']['done']

my_id = boards['work']['member_id']

# for member in client.get_board(work_board_id).all_members():
#     print("Name: %s, ID: %s\n" % (member.full_name, member.id))
