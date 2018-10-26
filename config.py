from ruamel.yaml import YAML
import logging

class Config(object):

    config_file = None
    yaml = None

    config = None

    trello_config = None
    cal_config = None


    def __init__(self):
        pass

    def init(self, cfile="config/config.yml"):
        self.config_file = cfile
        self.config = self.load_config(cfile=cfile)
        self.trello_config = self.get_config(["TRELLO"])
        self.cal_config = self.get_config(["CALENDAR"])


    def load_config(self, cfile="config/config.yml"):
        file = open(cfile,"r")
        self.yaml = YAML()
        result = self.yaml.load(file)
        file.close()
        return result

    def request_calendar(self):
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
        logging.info("Unsaved config looks like: %s", self.cal_config)


    def get_cal_url(self):
        if(self.cal_config == None):
            self.request_calendar()
        else:
            return self.make_cal_url()

    def make_cal_url(self):
        # url = "https://user:pass@hostname/caldav.php/"
        url = ("%s://%s:%s@%s" % (
            self.cal_config['protocol'],
            self.cal_config['user'],
            self.cal_config['password'],
            self.cal_config['url']))
        return url


    def get_api_info(self):
        api_key = self.trello_config['api_key']
        return api_key

    def save_token(self, out):
        self.write_config(['TRELLO', 'token'], out['token'])

    def get_token(self):
        token = self.get_config(['TRELLO', 'token'])
        return token

    def get_client(self):
        return [self.trello_config['api_key'],
            self.trello_config['api_secret'],
            self.trello_config['oauth_token'],
            self.trello_config['oauth_token_secret']]

    def get_config(self, position, configuration=None):
        if configuration == None:
            configuration = self.config
        value = configuration
        for nest in position:
            value = value[nest]
        return value

    def write_config(self, position, value):
    # TODO: allow an array of values to be written (so less writes)
        configuration = self.config
        last = position[-1]
        position = position[:-1]

        for nest in position:
            configuration = configuration[nest]

        configuration[last] = value

        file_w = open(self.config_file, "w")
        self.yaml.dump(self.config, file_w)
        file_w.close()



config = Config()
