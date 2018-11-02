import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from trello_client import t_client, db
import os

db.connect()
db.create_tables([t_client.LoggedCard])

conf_dir = "config"
if not os.path.exists(conf_dir):
    os.makedirs(conf_dir)
f = open("config/config.yml", "x")
