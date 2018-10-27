from ruamel.yaml import YAML
import logging

class Config(object):

    config_file = None
    yaml = None

    def __init__(self):
        self.config = dict()

    def init(self, cfile="config/config.yml"):
        self.config_file = cfile
        self.config = self.load_config(cfile=cfile)


    def load_config(self, cfile="config/config.yml"):
        file = open(cfile,"r")
        self.yaml = YAML()
        result = self.yaml.load(file)
        file.close()
        if result == None:
            result = dict()
        return result

    def request_calendar(self):
        print("hmmm... No calendar details found. Please fill out the form below.")
        protocol = input("protocol (http or https): ")
        url = input("url (without protocol): ")
        user = input("user:")
        password = input("password:")
        logging.info("Calendar requested and about save.")
        self.save_cal(protocol, url, user, password)


    def save_cal(self, protocol, url, user, password):
        self.write_config(['CALENDAR', 'protocol'], protocol)
        self.write_config(['CALENDAR', 'user'], user)
        self.write_config(['CALENDAR', 'password'], password)
        self.write_config(['CALENDAR', 'url'], url)


    def get_cal_url(self):
        if(self.get_config(['CALENDAR']) == None or
            self.get_config(['CALENDAR', 'protocol']) == None or
            self.get_config(['CALENDAR', 'user']) == None or
            self.get_config(['CALENDAR', 'password']) == None or
            self.get_config(['CALENDAR', 'url']) == None):
            self.request_calendar()
        return self.make_cal_url()

    def make_cal_url(self):
        # url = "https://user:pass@hostname/caldav.php/"
        url = ("%s://%s:%s@%s" % (
            self.get_config(['CALENDAR', 'protocol']),
            self.get_config(['CALENDAR', 'user']),
            self.get_config(['CALENDAR', 'password']),
            self.get_config(['CALENDAR', 'url'])))
        return url


    def get_api_info(self):
        api_key = self.get_config(['TRELLO','api_key'])
        return api_key

    def save_token(self, out):
        self.write_config(['TRELLO', 'token'], out['token'])

    def get_token(self):
        token = self.get_config(['TRELLO', 'token'])
        return token

    def get_client(self):
        return [self.get_config(['TRELLO','api_key']),
            self.get_config(['TRELLO','api_secret']),
            self.get_config(['TRELLO','oauth_token']),
            self.get_config(['TRELLO','oauth_token_secret'])]

    def get_config(self, position):

        configuration = self.config
        last = position.pop()

        if position:
            for nest in position:
                if (not configuration.__contains__(nest) or not configuration[nest]):
                    logging.info("config['%s'] is None or doesn't exist" % nest)
                    configuration[nest] = dict()
                    logging.info("config: %s\nself.config: %s" % (configuration,self.config) )

                logging.info("config: %s" % configuration)
                configuration = configuration[nest]

        if configuration.__contains__(last):
            return configuration[last]
        else:
            configuration[last] = None
            logging.info("writing conf: %s to file: %s" % (self.config, self.config_file) )
            self.write_to_config()
            return configuration[last]

    def write_to_config(self):
        file_w = open(self.config_file, "w")
        self.yaml.dump(self.config, file_w)
        file_w.close()

    def write_config(self, position, value):
    # TODO: allow an array of values to be written (so less writes)
        logging.info("write_config %s: %s" % (position,value))

        configuration = self.config
        last = position[-1]
        position = position[:-1]

        # missing_nesting = []
        for nest in position:
            if (not configuration.__contains__(nest) or configuration[nest] == None):
                configuration[nest] = dict()
            configuration = configuration[nest]

        configuration[last] = value

        self.write_to_config()
        logging.info("successfully wrote %s: %s" % (last,value))


config = Config()
