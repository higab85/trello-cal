from datetime import datetime, timedelta
import uuid
import logging
import caldav
# from caldav.elements import dav, cdav
import os
import sys
sys.path.insert(
        0,
        os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.trello_client import T_CLIENT
from app.config import CONFIG

logging.basicConfig(
    filename='trello_cal.log',
    filemode='w',
    level=logging.DEBUG,
    format='[%(asctime)s]%(levelname)s: %(message)s',
    datefmt='%H:%M:%S')

class Calendar_Client:

    hour = timedelta(hours=1)
    calendar = None

    def __init__(self):
        pass

    def init(self, config_file=None):
        if config_file is not None:
            logging.info(
                    "Initialising config %s from Calendar_Client.",
                    config_file)
            CONFIG.init(cfile=config_file)
        url = CONFIG.get_cal_url()
        logging.info("connecting to %s", url)
        try:
            client = caldav.DAVClient(url)
        except KeyError:
            CONFIG.request_calendar()
            client = caldav.DAVClient(CONFIG.get_cal_url())
        principal = client.principal()
        calendars = principal.calendars()
        if calendars:
            self.calendar = calendars[0]

    def add_to_calendar(self, vcal):
        event = self.calendar.add_event(vcal)
        logging.info("Event %s added to calendar.", event)

    @staticmethod
    def build_vcal(start, end, title, description, stamp=None, uid=None):
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
                    title.replace("\n", "\\n"),
                    description.replace("\n", "\\n"))
        logging.info("VCAL created: %s", vcal)
        return vcal

    def make_vcal(self, card):
        title = card.name
        description = T_CLIENT.get_description(card)
        duration = self.hour
        try:
            end = card.listCardMove_date()[0][-1]
        except IndexError:
            end = card.card_created_date
        start = end - duration
        logging.info("vcal end:%s", end)
        return self.build_vcal(start, end, title, description)

    def event_to_cal(self, card):
        logging.info("event_to_vcal()")
        vcal = self.make_vcal(card)
        self.add_to_calendar(vcal)


C_CLIENT = Calendar_Client()
