import unittest
from shutil import copyfile
from config import config
import logging
import os

logging.basicConfig(filename='test.log', filemode='w', level=logging.DEBUG, format='[%(asctime)s]%(levelname)s: %(message)s', datefmt='%H:%M:%S')

class TestConfig(unittest.TestCase):

    def setUp(self):
        self.conf_file = "config/config.test.yml.tmp"
        copyfile("config/config.test.yml", self.conf_file)
        config.init(cfile=self.conf_file)

    def tearDown(self):
        os.remove(self.conf_file)

    def test_load_correct_config(self):
        value = config.get_config(["CALENDAR","user"])
        self.assertEqual(value, "test")

    def test_trello_config(self):
        value = config.get_config(["TRELLO", "boards", "default", "id"])
        self.assertEqual(value, "5bd9b0bbf266e64d059403fa")

    def test_write_config_running(self):
        config.write_config(["CALENDAR","user"], "flamingo")
        value = config.get_config(["CALENDAR","user"])
        self.assertEqual(value, "flamingo")

    def test_write_config_running_single_inexistant_field(self):
        config.write_config(["CALENDAR","colour"], "pink")
        value = config.get_config(["CALENDAR","colour"])
        self.assertEqual(value, "pink")

    def test_write_config_running_multi_inexistant_field(self):
        config.write_config(["CALENDAR", "box", "colour", "id"], "5")
        value = config.get_config(["CALENDAR", "box", "colour", "id"])
        self.assertEqual(value, "5")

    def test_write_config_saved_to_disc(self):
        config.write_config(["CALENDAR","user"], "flamingo")
        config.load_config(self.conf_file)
        value = config.get_config(["CALENDAR","user"])
        self.assertEqual(value, "flamingo")

if __name__ == '__main__':
    unittest.main()
