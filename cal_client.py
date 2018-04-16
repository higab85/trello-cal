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
