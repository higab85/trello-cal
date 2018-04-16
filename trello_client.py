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
# [3.(for list id) print(client.get_board(work_board_id).open_lists()[3].id) ]
boards = trello_config['boards']

personal_board_id  = boards['personal']['id']
personal_board_done_list_id = boards['personal']['lists']['done']

work_board_id  = boards['work']['id']
work_board_done_list_id = boards['work']['lists']['done']

# for member in client.get_board(work_board_id).all_members():
#     print("Name: %s, ID: %s\n" % (member.full_name, member.id))
