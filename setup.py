from trello_client import t_client, db

db.connect()
db.create_tables([t_client.LoggedCard])
