from trello import TrelloClient

import yaml

with open('config.yml') as c:
    config = yaml.load(c)
trello_config = config['TRELLO']


client = TrelloClient(
    api_key=trello_config['api_key'],
    api_secret=trello_config['api_secret'],
    token=trello_config['oauth_token'],
    token_secret=trello_config['oauth_token_secret']
)

## Get a board ID like so:
# 1. client.list_boards()
# 2. client.listboards()[number of board].id
boards = trello_config['boards']
personal_board_id  = boards['personal']['id']
personal_board_done_list_id = boards['personal']['lists']['done']
