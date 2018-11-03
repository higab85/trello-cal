import os
import sys
sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from trello import TrelloClient, exceptions
from peewee import (
    Model, CharField, DateField, SqliteDatabase, DoesNotExist, Proxy)
from datetime import datetime
import hashlib
from app.config import CONFIG
import logging

db_proxy = Proxy()
logging.basicConfig(
    filename='trello_cal.log', filemode='w',
    level=logging.DEBUG,
    format='[%(asctime)s]%(levelname)s: %(message)s',
    datefmt='%H:%M:%S')


class Trello_Client:

    def __init__(self, database=None):
        self.connection_tries = 0
        self.client = None
        self.api_key = None
        self.token = None
        if database is None:
            database = 'sent_to_cal.db'
        if not os.path.exists(database):
            open(database, "x")
        global db_proxy
        db = SqliteDatabase(database)
        db_proxy.initialize(db)
        db_proxy.create_tables([self.LoggedCard])
        logging.info("db: %s", db_proxy)

    def init(self):
        logging.info("trello_client init")
        self.login()
        # self.client = TrelloClient(config.get_client())

    def boards(self):
        return CONFIG.get_config(['TRELLO', 'boards']) or dict()

    def refresh_credentials(self):
        logging.warning("Unauthorized. Client: %s", self.client)

        print("Time to refresh credentials!")
        print("Log in to trello at https://trello.com,\
            then visit https://trello.com/app-key")

        self.api_key = input("Trello API key: ")
        CONFIG.write_config(["TRELLO", "api_key"], self.api_key)

        self.token = input("Trello token: ")
        CONFIG.write_config(["TRELLO", "token"], self.token)

        self.login_petition()

    def login_petition(self):
        self.client = TrelloClient(self.api_key, token=self.token)

    def is_logged_in(self):
        try:
            self.client.list_boards()
            return True
        except exceptions.Unauthorized:
            logging.warning("Not authorised")
        logging.warning("Not logged in")
        return False

    def login(self):
        logging.info("Trying to log in.")

        # GET API INFO
        self.api_key = CONFIG.get_api_info()
        self.token = CONFIG.get_token()
        if(self.api_key is None or self.token is None):
            self.refresh_credentials()
            return
        logging.info(
            "Trello API key and token: %s", [self.api_key, self.token])

        if self.connection_tries > 1:
            self.refresh_credentials()
            return
        self.connection_tries += 1
        logging.info("Connections tries: %s", self.connection_tries)

        self.login_petition()
        if self.is_logged_in():
            logging.info("Log in successful")
            self.connection_tries = 0
        else:
            logging.warning("Login failed.")
            self.login()

    class LoggedCard(Model):
        card_id = CharField()
        card_hash = CharField()
        datetime_added = DateField()
        session_id = CharField()

        def __string__(self):
            return (
                self.card_id, "\n",
                self.card_hash, "\n",
                self.datetime_added, "\n",
                self.session_id)

        class Meta:
            database = db_proxy

    def archive_card(self, card):
        card.set_closed(True)

    def build_checklist(self, checklists):
        checklists_out = ""
        for checklist in checklists:
            checklists_out += "\nCHECKLIST: " + checklist.name + "\n"
            for item in checklist.items:
                checklists_out += "- " + item['name'] + "\n"
        return checklists_out

    def get_checklists(self, card):
        checklists = card.fetch_checklists()
        checklists_out = self.build_checklist(checklists)
        return checklists_out

    def get_description(self, card):
        checklists = self.get_checklists(card)
        if checklists:
            return card.description + "\n" + checklists
        return card.description

    def card_hash(self, card):
        hashable = self.get_description(card)
        return hashlib.sha256(hashable.encode()).hexdigest()

# TEST ME
    def log__card(self, card_id, card_hash, datetime_added, session_id):
        self.LoggedCard.create(
            card_id=card_id,
            card_hash=card_hash,
            datetime_added=datetime_added,
            session_id=session_id)
        logging.info("Logged card_id: %s", card_id)

    def log_card(self, card, session):
        self.log__card(card.id, self.card_hash(card), datetime.now(), session)

# TEST ME
    def is__new_card(self, card_id, card_name):
        try:
            self.LoggedCard.get(self.LoggedCard.card_id == card_id)
        except DoesNotExist:
            message = "New card: %s" % card_name
            logging.info(message)
            logging.info("New card_id: %s", card_id)
            print(message)
            return True
        return False

    def is_new_card(self, card):
        return self.is__new_card(card.id, card.name)

    def get_list_cards(self, board_id, list_id, members=[]):
        logging.info(
            "Getting list %s from board %s with members %s",
            list_id, board_id, members)
        cards = self.client.get_board(board_id).get_list(list_id).list_cards()
        return filter(lambda x: x.member_id == members, cards)

# TEST ME
    def board_to_yaml(self, name, board_id):
        CONFIG.write_config(['TRELLO', 'boards', name, 'id'], board_id)

# TEST ME
    def find__board_id(self, board_name, boards):
        logging.warning("You don't seem to have a %s b, board!", board_name)
        logging.info("Available boards: %s", boards)
        for board_id, board in enumerate(boards):
            print("%s:%s" % (board_id, board))
        board_num = int(input("What is the id of your %s board?" % board_name))
        board_id = boards[board_num].id
        self.board_to_yaml(board_name, board_id)
        return board_id

    def find_board_id(self, board_name):
        boards = self.client.list_boards()
        return self.find__board_id(board_name, boards)

# TEST ME
    def get_board_id(self, board_name):
        try:
            if self.boards()[board_name]['id'] is None:
                return self.find_board_id(board_name)
            return self.boards()[board_name]['id']
        except (KeyError, exceptions.ResourceUnavailable) as e:
            logging.warning("Exception %s at get_board_id", e)
            CONFIG.get_config(['TRELLO', 'boards', board_name, 'id'])
            return self.get_board_id(board_name)

# TEST ME
    def list_to_yaml(self, board_name, list_name, list_id):
        CONFIG.write_config(
            ['TRELLO', 'boards', board_name, list_name, 'id'], list_id)

    def find_list_id(self, board_config, board_name, list_name):
        logging.warning(
            "You don't seem to have a %s list, on your this board!\
            Please select one of the following: ", list_name)
        board_id = str(board_config['id'])
        for elist_id, elist_name in enumerate(
                self.client.get_board(board_id).open_lists()):
            print("%s:%s" % (elist_id, elist_name))
        list_num = int(input("What is the id of your %s list?" % (list_name)))
        list_id = self.client.get_board(board_id).open_lists()[list_num].id
        self.list_to_yaml(board_config, board_name, list_name, list_id)
        return list_id

# TEST ME
    def get_list_id(self, board_name, list_name):
        board_config = self.boards()[board_name]
        try:
            if board_config[list_name] is None:
                return self.find_list_id(board_config, board_name, list_name)
            return self.boards()[board_name][list_name]["id"]
        except KeyError:
            CONFIG.get_config(['TRELLO', 'boards', board_name, list_name])
            return self.get_list_id(board_name, list_name)


T_CLIENT = Trello_Client()

# Get a board ID like so:
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
