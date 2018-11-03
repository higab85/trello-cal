import datetime
from shutil import copyfile
import os
import unittest
from mock import patch
from app.config import CONFIG
from app.trello_client import Trello_Client


class TestTrelloClient(unittest.TestCase):

    class CheckList:
        def build(self, list):
            for item in list:
                checklist_item = dict()
                checklist_item["name"] = item
                self.items.append(checklist_item)

        def __init__(self, name, list):
            self.name = name
            self.items = []
            self.build(list)

    def setUp(self):
        self.conf_file = "config/config.test.yml.tmp"
        self.db_file = 'test_sent_to_cal.db'

        self.t_client = Trello_Client(self.db_file)

        copyfile("config/config.test.yml", self.conf_file)
        CONFIG.init(self.conf_file)

    def tearDown(self):
        os.remove(self.conf_file)
        os.remove(self.db_file)

    @patch('app.trello_client.Trello_Client.refresh_credentials')
    def test_login__no_api_key(self, mock):
        CONFIG.write_config(['TRELLO', 'api_key'], None)
        self.t_client.login()
        self.assertTrue(mock.called)

    @patch('app.trello_client.Trello_Client.refresh_credentials')
    def test_login__no_token(self, mock):
        CONFIG.write_config(['TRELLO', 'token'], None)
        self.t_client.login()
        self.assertTrue(mock.called)

    @patch('app.trello_client.Trello_Client.refresh_credentials')
    def test_login__wrong_credentials(self, mock):
        CONFIG.write_config(['TRELLO', 'token'], "1")
        self.t_client.login()
        self.assertTrue(mock.called)

    def test_build_checklist(self):
        list1 = ["banana", "apple", "peach"]
        list2 = ["cats", "dogs", "gerbils", "bears", "birds"]

        checklist1 = self.CheckList("fruits", list1)
        checklist2 = self.CheckList("animals", list2)
        built_checklist = self.t_client.build_checklist(
            [checklist1, checklist2])
        control_checklist = """\nCHECKLIST: fruits
- banana
- apple
- peach
\nCHECKLIST: animals
- cats
- dogs
- gerbils
- bears
- birds\n"""
        self.assertEqual(built_checklist, control_checklist)

    def test_log_card__new(self):
        now = datetime.datetime.now()
        card_id = "1"
        card_hash = "2"
        session_id = "3"
        self.t_client.log__card(card_id, card_hash, now, session_id)
        new_card = self.t_client.is__new_card(card_id, card_hash)
        self.assertFalse(new_card)

    def test_log_card__fake(self):
        card_id = "4"
        card_hash = "5"
        new_card = self.t_client.is__new_card(card_id, card_hash)
        self.assertTrue(new_card)


if __name__ == '__main__':
    unittest.main()
