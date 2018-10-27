from datetime import datetime, timedelta
import caldav
import uuid
from caldav.elements import dav, cdav
from trello_client import t_client
from config import config
import logging

logging.basicConfig(filename='trello_cal.log', filemode='w', level=logging.DEBUG, format='[%(asctime)s]%(levelname)s: %(message)s', datefmt='%H:%M:%S')

class Calendar_Client(object):

    hour = timedelta(hours=1)
    calendar = None

    def __init__(self):
        pass

    def init(self, config_file=None):
        if config_file is not None:
            logging.info("Initialising config %s from Calendar_Client.", config_file)
            config.init(cfile=config_file)
        url = config.get_cal_url()
        logging.info("connecting to %s", url)
        try:
            client = caldav.DAVClient(url)
        except KeyError:
            config.request_calendar()
            client = caldav.DAVClient(config.get_cal_url())
        principal = client.principal()
        calendars = principal.calendars()
        if len(calendars) > 0:
            self.calendar = calendars[0]

    def add_to_calendar(self, vcal):
        event = self.calendar.add_event(vcal)
        logging.info("Event %s added to calendar.", event)

    def _make_vcal(self, start, end, title, description, stamp=None, uid=None):
        if stamp is None:
            stamp = datetime.now()
        if uid is None:
            uid = uuid.uuid1().int

        # description = description.replace("\r\n", "\\n")
        # description = description.replace("\n", "\\n")

        logging.info("vcal being built from - start:%s, end:%s, title:%s, description:%s", start, end, title, description)
        vcal =  """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Example Corp.//CalDAV Client//EN
BEGIN:VEVENT
UID:%s
DTSTAMP:%s
DTSTART:%s
DTEND:%s
SUMMARY;ENCODING=quoted-printable:%s
DESCRIPTION;ENCODING=quoted-printable:%s
END:VEVENT
END:VCALENDAR""" % (uid,
        stamp.strftime("%Y%m%dT%H%M%SZ"),
        start.strftime("%Y%m%dT%H%M%SZ"),
        end.strftime("%Y%m%dT%H%M%SZ"),
        title.replace("\n","\\n"),
        description.replace("\n","\\n"))
        logging.info("VCAL created: %s",vcal)
        return vcal

    def make_vcal(self, card):
        title = card.name
        description = t_client.get_description(card)
        duration = self.hour
        try:
            end = card.listCardMove_date()[0][-1]
        except IndexError:
            end = card.card_created_date
        start = end - duration
        logging.info("vcal end:%s", end)
        return self._make_vcal(start, end, title, description)

    def event_to_cal(self, card):
        logging.info("event_to_vcal()")
        vcal = self.make_vcal(card)
        self.add_to_calendar(vcal)

c_client = Calendar_Client()
