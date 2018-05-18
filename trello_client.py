from trello import TrelloClient, util
from ruamel.yaml import YAML
from peewee import *
from datetime import date,datetime
import hashlib
import uuid
from pprint import pprint
from config import config

class Trello_Client(object):

    client = None

    def __init__(self):
        pass

    def init(self):
        self.client = TrelloClient(config.get_client())

    def boards(self):
        return config.trello_config['boards']

    def login(self):
        api_key, api_secret = config.get_api_info()
        print("API: %s" % [api_key, api_secret])
        token, token_secret = config.get_token()
        try:
            self.client = TrelloClient(api_key,
                api_secret=api_secret,
                token=token,
                token_secret=token_secret)
        except exceptions.Unauthorized:
            out = util.create_oauth_token(key=api_key, secret=api_secret)
            print("token: %s" % out)
            config.save_token(out)


    class LoggedCard(Model):
        card_id = CharField()
        card_hash = CharField()
        datetime_added = DateField()
        session_id = CharField()

        def __string__(self):
            return (
                self.card_id,"\n",
                self.card_hash,"\n",
                self.datetime_added,"\n",
                self.session_id)

        class Meta:
            database = SqliteDatabase('sent_to_cal.db')

    def archive_card(self, card):
        card.set_closed(True)

    def get_checklists(self, card):
        checklists = card.fetch_checklists()
        checklist_out = ""
        for checklist in checklists:
            checklist_out += "\nCHECKLIST: " + checklist.name +"\n"
            for item in checklist.items:
                checklist_out += "- " + item['name'] + "\n"
        return checklist_out

    def get_description(self, card):
        return card.description + "\n" + self.get_checklists(card)


    def pretty_print(self, card):
        print("Title: %s:\nDescription:%s\nFinished at:%s\n\n" % (
            card.name,
            self.get_description(card),
            card.listCardMove_date()[0][-1]))

    def card_hash(self, card):
        hashable = self.get_description(card)
        return hashlib.sha256(hashable.encode()).hexdigest()

    def log_card(self, card, session):
        event = self.LoggedCard.create(
            card_id = card.id,
            card_hash = self.card_hash(card),
            datetime_added = datetime.now(),
            session_id = session)

    def is_new_card(self, card):
        try:
            self.LoggedCard.get(self.LoggedCard.card_id == card.id)
        except DoesNotExist:
            print("New card:", card.name)
            return True
        return False

    def get_list_cards(self, board_id, list_id, members=[]):
        print("Getting list %s from board %s with members %s" % (list_id, board_id, members))
        print("API KEY(t_c): %s" % self.client.api_key)
        cards = self.client.get_board(board_id).get_list(list_id).list_cards()
        return filter(lambda x: x.member_id == members, cards)

    def board_to_yaml(self, name, board_id):
        config.write_config(['TRELLO','boards', name, 'id'], board_id)
        print("'%s' details written to config" % name)

    def find_board_id(self, board_name):
        print("You don't seem to have a %s board! \n\
    Please select one of the following: " % board_name)
        for id,board in enumerate(self.client.list_boards()):
            print("%s:%s" % (id, board))
        board_num = int(input("What is the id of your %s board?" % (board_name)))
        board_id = self.client.list_boards()[board_num].id
        board_to_yaml(board_name, board_id)
        return board_id

    def get_board_id(self, board_name):
        print("getting board id!")
        if self.boards()[board_name]['id'] == None:
            return self.find_board_id(board_name)
        else:
            return self.boards()[board_name]['id']

    def list_to_yaml(self, board_name, list_name, list_id):
        config.write_config(['TRELLO','boards', board_name, list_name], list_id)
        print("%s id has been written to config" % list_name)

    def find_list_id(self, board_config, list_name):
        print("You don't seem to have a %s list, on your this board! \n\
    Please select one of the following: " % list_name)
        board_id = str(board_config['id'])
        board_name = board_config['name']
        for id,list in enumerate(self.client.get_board(board_id).open_lists()):
            print("%s:%s" % (id, list))
        list_num = int(input("What is the id of your %s list?" % (list_name)))
        list_id = self.client.get_board(board_id).open_lists()[list_num].id
        list_to_yaml(board_name, list_name, list_id)
        return list_id

    def get_list_id(self, board_name, list_name):
        board_config = self.boards()[board_name]
        if board_config[list_name] == None:
            return self.find_list_id(board_config, list_name)
        else:
            return self.boards()[board_name][list_name]

t_client = Trello_Client()

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
