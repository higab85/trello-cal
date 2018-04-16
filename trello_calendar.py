from datetime import datetime, timedelta
import caldav
from caldav.elements import dav, cdav
import uuid

from trello import TrelloClient

import yaml

with open('config.yml') as c:
    config = yaml.load(c)
cal_config = config['CALENDAR']
trello_config = config['TRELLO']

###############
### CALDAV
###############


# url = "https://user:pass@hostname/caldav.php/"
url = ("%s://%s:%s@%s" % (cal_config['protocol'],cal_config['user'],cal_config['password'],cal_config['url']))
print("connecting to",url)

client = caldav.DAVClient(url)
principal = client.principal()
calendars = principal.calendars()
calendar = None
if len(calendars) > 0:
    calendar = calendars[0]

# constants
hour = timedelta(hours=1)

def make_event(end, duration, title, description=""):
    vcal =  """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Example Corp.//CalDAV Client//EN
BEGIN:VEVENT
UID:%s
DTSTAMP:%s
DTSTART:%s
DTEND:%s
SUMMARY:%s
DESCRIPTION:%s
END:VEVENT
END:VCALENDAR""" % (uuid.uuid1().int,
    datetime.now().strftime("%Y%m%dT%H%M%SZ"),
    (end-duration).strftime("%Y%m%dT%H%M%SZ"),
    end.strftime("%Y%m%dT%H%M%SZ"),
    title,
    description)
    event = calendar.add_event(vcal)
    print("Event", event, "created")



###############
### Trello
###############

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

all_cards_in_done = client.get_board(personal_board_id).get_list(personal_board_done_list_id).list_cards()

for card in all_cards_in_done:
    name = card.name
    description = card.description
    end = card.listCardMove_date()[0][-1]
    print("Title: %s:\nDescription: %s\nFinished at:%s\n\n" % (name, description,end))
    make_event(end,hour,name,description)
    card.set_closed(True)
