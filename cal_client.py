from datetime import datetime, timedelta
import caldav
import uuid
from caldav.elements import dav, cdav

import yaml

with open('config.yml') as c:
    config = yaml.load(c)
cal_config = config['CALENDAR']

###############
### CALDAV
###############


# url = "https://user:pass@hostname/caldav.php/"
url = ("%s://%s:%s@%s" % (
    cal_config['protocol'],
    cal_config['user'],
    cal_config['password'],
    cal_config['url']))
print("connecting to",url)

client = caldav.DAVClient(url)
principal = client.principal()
calendars = principal.calendars()
calendar = None
if len(calendars) > 0:
    calendar = calendars[0]

# constants
hour = timedelta(hours=1)

def checklist_print(checklists):
    checklist_out = ""
    for checklist in checklists:
        checklist_out += "\nCHECKLIST: " + checklist.name +"\n"
        for item in checklist.items:
            checklist_out += "- " + item['name'] + "\n"
    return checklist_out


def pretty_print(card):
    print("Title: %s:\nDescription: %s\n%s\nFinished at:%s\n\n" % (
        card.name,
        card.description,
        checklist_print(card.fetch_checklists()),
        card.listCardMove_date()[0][-1]))

def make_event(card):
    title = card.name
    description = card.description + "\n"  + checklist_print(card.fetch_checklists())
    duration = hour
    end = card.listCardMove_date()[0][-1]
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
    (end-duration).strftime("%Y%m%dT%H%M%SZ"),
    end.strftime("%Y%m%dT%H%M%SZ"),
    title,
    description.replace("\n","=0D=0A"))
    print("VCAL:\n",vcal)
    event = calendar.add_event(vcal)
    print("Event", event, "created")
