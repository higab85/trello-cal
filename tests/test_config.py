import os
import unittest
from shutil import copyfile
from app.config import CONFIG
import logging

logging.basicConfig(filename='test.log', filemode='w', level=logging.DEBUG, format='[%(asctime)s]%(levelname)s: %(message)s', datefmt='%H:%M:%S')

class TestConfig(unittest.TestCase):

    def setUp(self):
        self.conf_file = "config/config.test.yml.tmp"
        copyfile("config/config.test.yml", self.conf_file)
        CONFIG.init(cfile=self.conf_file)

    def tearDown(self):
        os.remove(self.conf_file)

    def test_load_correct_config(self):
        value = CONFIG.get_config(["CALENDAR","user"])
        self.assertEqual(value, "test")

    def test_trello_config(self):
        value = CONFIG.get_config(["TRELLO", "boards", "default", "id"])
        self.assertEqual(value, "5bd9b0bbf266e64d059403fa")

    def test_write_config_running(self):
        CONFIG.write_config(["CALENDAR","user"], "flamingo")
        value = CONFIG.get_config(["CALENDAR","user"])
        self.assertEqual(value, "flamingo")

    def test_write_config_running_single_inexistant_field(self):
        CONFIG.write_config(["CALENDAR","colour"], "pink")
        value = CONFIG.get_config(["CALENDAR","colour"])
        self.assertEqual(value, "pink")

    def test_write_config_running_multi_inexistant_field(self):
        CONFIG.write_config(["CALENDAR", "box", "colour", "id"], "5")
        value = CONFIG.get_config(["CALENDAR", "box", "colour", "id"])
        self.assertEqual(value, "5")

    def test_write_config_saved_to_disc(self):
        CONFIG.write_config(["CALENDAR","user"], "flamingo")
        CONFIG.load_config(self.conf_file)
        value = CONFIG.get_config(["CALENDAR","user"])
        self.assertEqual(value, "flamingo")

if __name__ == '__main__':
    unittest.main()
