from trello_client import db,LoggedCard

db.connect()
db.create_tables([LoggedCard])
