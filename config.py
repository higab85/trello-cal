from ruamel.yaml import YAML


class Config(object):

    config_file = None
    yaml = None

    config = None

    trello_config = None
    cal_config = None


    def __init__(self):
        pass

    def init(self, cfile="config.yml"):
        self.config_file = cfile
        self.config = self.load_config(cfile)
        self.trello_config = self.get_config(["TRELLO"])
        self.cal_config = self.get_config(["CALENDAR"])


    def load_config(self, conf_file="config.yml"):
        file = open(conf_file,"r")
        self.yaml = YAML()
        return self.yaml.load(file)

    def request_calendar():
        protocol = input("protocol (http or https): ")
        url = input("url (without protocol): ")
        user = input("user:")
        password = input("password:")
        self.save_cal(protocol, url, user, password)


    def save_cal(self, protocol, url, user, password):
        self.cal_config['protocol'] = protocol
        self.cal_config['user'] = user
        self.cal_config['password'] = password
        self.cal_config['url'] = url
        file_w = open("config.yml", "w")
        self.yaml.dump(config, file_w)
        file_w.close()


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
        api_secret = self.trello_config['api_secret']
        return [api_key, api_secret]

    def save_token(self, out):
        self.write_config(['TRELLO', 'oauth_token'], out['oauth_token'])
        self.write_config(['TRELLO', 'oauth_token_secret'], out['oauth_token_secret'])

    def get_token(self):
        token = self.get_config(['TRELLO', 'oauth_token'])
        token_secret = self.get_config(['TRELLO', 'oauth_token_secret'])
        return token, token_secret

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
