from datetime import datetime, timedelta
import caldav
import uuid
from caldav.elements import dav, cdav
from trello_client import t_client
from config import config


class Calendar_Client(object):

    hour = timedelta(hours=1)
    calendar = None

    def __init__(self):
        pass

    def init(self):
        url = config.get_cal_url()
        print("connecting to",url)
        client = caldav.DAVClient(url)
        principal = client.principal()
        calendars = principal.calendars()
        if len(calendars) > 0:
            self.calendar = calendars[0]

    def add_to_calendar(self, vcal):
        event = self.calendar.add_event(vcal)
        print("Event", event, "added to calendar.")

    def _make_vcal(self, start, end, title, description):
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

    def make_vcal(self, card):
        title = card.name
        description = t_client.get_description(card)
        duration = self.hour
        end = card.listCardMove_date()[0][-1]
        start = end - duration
        return self._make_vcal(start, end, title, description)

    def event_to_cal(self, card):
        vcal = self.make_vcal(card)
        self.add_to_calendar(vcal)

c_client = Calendar_Client()
