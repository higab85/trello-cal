import unittest
from shutil import copyfile
from config import config
import logging
import os

class TestConfig(unittest.TestCase):

    def setUp(self):
        copyfile("config/config.test.yml", "config/config.test.yml.tmp")
        config.init(cfile="config/config.test.yml.tmp")

    def tearDown(self):
        os.remove("config/config.test.yml.tmp")

    def test_load_correct_config(self):
        value = config.get_config(["CALENDAR","user"])
        self.assertEqual(value, "bear")

    def test_trello_config(self):
        value = config.get_config(["boards", "personal", "id"], config.trello_config)
        self.assertEqual(value, "588644194fe4c310458d19f7")

    def test_write_config_running(self):
        config.write_config(["CALENDAR","user"], "flamingo")
        value = config.get_config(["CALENDAR","user"])
        self.assertEqual(value, "flamingo")

    def test_write_config_saved_to_disc(self):
        config.write_config(["CALENDAR","user"], "flamingo")
        config.load_config()
        value = config.get_config(["CALENDAR","user"])
        self.assertEqual(value, "flamingo")

if __name__ == '__main__':
    unittest.main()