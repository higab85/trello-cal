from trello import TrelloClient, util
from ruamel.yaml import YAML
from peewee import *
from datetime import date,datetime
import hashlib
import uuid
from pprint import pprint
from config import config
import logging
import sys

db = SqliteDatabase('sent_to_cal.db')

class Trello_Client(object):

    def __init__(self):
        self.connection_tries = 0
        self.client = None
        self.db = db


    def init(self):
        logging.info("trello_client init")
        self.login()
        # self.client = TrelloClient(config.get_client())


    def boards(self):
        return config.trello_config['boards']

    def refresh_credentials(self):
        logging.warning("Unauthorized. Client: %s" % self.client)

        print("Time to refresh credentials!")
        print("Visit https://trello.com/app-key")

        api_key = input("Trello API key: ")
        config.write_config(["TRELLO", "api_key"], api_key)

        token = input("Trello token: ")
        config.write_config(["TRELLO", "token"], token)

        self.login_petition(api_key, token)

    def login_petition(self, api_key, token):
        self.client = TrelloClient(api_key, token=token)
        logging.info("client: %s" % self.client )

    def login(self):
        logging.info("Trying to log in.")

        # GET API INFO
        api_key = config.get_api_info()
        token = config.get_token()
        logging.info("Trello API key and token: %s" % [api_key, token])

        if self.connection_tries > 3:
            self.refresh_credentials()
        self.connection_tries += 1
        try:
            self.login_petition(api_key, token)
        except exceptions.Unauthorized:
            logging.warn("Exception: %s" % sys.exc_info()[0])
            self.refresh_credentials()

        logging.info("Login successful")
        self.connection_tries = 0




        # api_secret = input("Trello API secret: ")
        # config.write_config(["TRELLO", "api_secret"], api_secret)
        #
        # logging.info("New Trello API key and secret %s" % [api_key, api_secret])

        # GET OATH INFO
        # token, token_secret = config.get_token()
        # logging.info("Old OAuth token, OAuth token secret: %s" % [token, token_secret])

        # token = input("Trello OAuth token: ")
        # config.write_config(["TRELLO", "oauth_token"], token)
        #
        # token_secret = input("Trello OAuth token secret: ")
        # config.write_config(["TRELLO", "oauth_token_secret"], token_secret)
        #
        # logging.info("New OAuth token, OAuth token secret: %s" % [token, token_secret])



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
            database = db

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
        out = "Title: %s:\nDescription:%s\nFinished at:%s\n\n" % (
            card.name,
            self.get_description(card),
            card.listCardMove_date()[0][-1])
        logging.info(out)
        print(out)

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
            message = "New card: " + card.name
            logging.info(message)
            print(message)
            return True
        return False

    def get_list_cards(self, board_id, list_id, members=[]):
        logging.info("Getting list %s from board %s with members %s" % (list_id, board_id, members))
        cards = self.client.get_board(board_id).get_list(list_id).list_cards()
        return filter(lambda x: x.member_id == members, cards)

    def board_to_yaml(self, name, board_id):
        config.write_config(['TRELLO','boards', name, 'id'], board_id)
        logging.info("'%s' details written to config" % name)

    def find_board_id(self, board_name):
        logging.warn("You don't seem to have a %s board! \n\
            Please select one of the following: " % board_name)
        boards = self.client.list_boards()
        logging.info("boards: %s" % boards)
        for id,board in enumerate(boards):
            print("%s:%s" % (id, board))
        board_num = int(input("What is the id of your %s board?" % (board_name)))
        board_id = boards[board_num].id
        self.board_to_yaml(board_name, board_id)
        return board_id

    def get_board_id(self, board_name):
        if self.boards()[board_name]['id'] == None:
            return self.find_board_id(board_name)
        else:
            return self.boards()[board_name]['id']

    def list_to_yaml(self, board_config, board_name, list_name, list_id):
        logging.info("%s id will be written to %s" %
            (list_id, config.config))
        config.write_config(['TRELLO','boards', board_name, list_name, 'id'], list_id)
        logging.info("%s id has been written to config" % list_name)

    def find_list_id(self, board_config, board_name, list_name):
        logging.warn("You don't seem to have a %s list, on your this board! Please select one of the following: " % list_name)
        board_id = str(board_config['id'])
        for id,list in enumerate(self.client.get_board(board_id).open_lists()):
            print("%s:%s" % (id, list))
        list_num = int(input("What is the id of your %s list?" % (list_name)))
        list_id = self.client.get_board(board_id).open_lists()[list_num].id
        self.list_to_yaml(board_config, board_name, list_name, list_id)
        return list_id

    def get_list_id(self, board_name, list_name):
        board_config = self.boards()[board_name]
        if board_config[list_name] == None:
            return self.find_list_id(board_config, board_name, list_name)
        else:
            return self.boards()[board_name][list_name]["id"]

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
