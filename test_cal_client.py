from cal_client import c_client
import unittest
import datetime
from shutil import copyfile
import os


class TestCalClient(unittest.TestCase):

    def setUp(self):
        self.conf_file = "config/config.test.yml.tmp"
        copyfile("config/config.test.yml", self.conf_file)
        c_client.init(self.conf_file)

    def tearDown(self):
        os.remove(self.conf_file)

    def test_vcal_built_correctly(self):
        uid = 5
        stamp = datetime.datetime.now()
        start = stamp + datetime.timedelta(hours=-4)
        finish = start + datetime.timedelta(hours=2)
        title = """Cat
Life"""
        description = """The cat was
oh so sad.

She cried like mad.
"""
        correct_vcal = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Example Corp.//CalDAV Client//EN
BEGIN:VEVENT
UID:%s
DTSTAMP:%s
DTSTART:%s
DTEND:%s
SUMMARY;ENCODING=quoted-printable:Cat\\nLife
DESCRIPTION;ENCODING=quoted-printable:The cat was\\noh so sad.\\n\\nShe cried like mad.\\n
END:VEVENT
END:VCALENDAR""" % (uid, stamp.strftime("%Y%m%dT%H%M%SZ"), start.strftime("%Y%m%dT%H%M%SZ"), finish.strftime("%Y%m%dT%H%M%SZ"))
        fn_vcal = c_client._make_vcal(start, finish, title, description, stamp=stamp, uid=uid)
        self.assertEqual(correct_vcal, fn_vcal)


if __name__ == '__main__':
    unittest.main()
