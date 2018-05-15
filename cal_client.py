from datetime import datetime, timedelta
import caldav
import uuid
from caldav.elements import dav, cdav
from trello_client import get_description
from config import save_cal, cal_url as url


###############
### CALDAV
###############

print("connecting to",url)

client = caldav.DAVClient(url)
principal = client.principal()
calendars = principal.calendars()
calendar = None
if len(calendars) > 0:
    calendar = calendars[0]

# constants
hour = timedelta(hours=1)

def request_calendar():
    protocol = input("protocol (http or https): ")
    url = input("url (without protocol): ")
    user = input("user:")
    password = input("password:")
    save_cal(protocol, url, user, password)


def add_to_calendar(vcal):
    event = calendar.add_event(vcal)
    print("Event", event, "added to calendar.")

def _make_vcal(start, end, title, description):
    vcal =  """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Example Corp.//CalDAV Client//EN
BEGIN:VEVENT
UID:%s
DTSTAMP:%s
DTSTART:%s
DTEND:%s
SUMMARY:%s
DESCRIPTION;ENCODING=QUOTED-PRINTABLE:%s
END:VEVENT
END:VCALENDAR""" % (uuid.uuid1().int,
    datetime.now().strftime("%Y%m%dT%H%M%SZ"),
    start.strftime("%Y%m%dT%H%M%SZ"),
    end.strftime("%Y%m%dT%H%M%SZ"),
    title,
    description.replace("\n","=0D=0A"))
    print("VCAL created:\n",vcal)
    return vcal

def make_vcal(card):
    title = card.name
    description = get_description(card)
    duration = hour
    end = card.listCardMove_date()[0][-1]
    start = end - duration
    return _make_vcal(start, end, title, description)

def event_to_cal(card):
    vcal = make_vcal(card)
    add_to_calendar(vcal)
