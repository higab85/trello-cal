from ruamel.yaml import YAML

# cal_config = config['CALENDAR']
# cal_url = get_cal_url()
class Config():

    config_file = None
    yaml = None

    config = None

    trello_config = None
    cal_config = None

    def __init__(self, cfile="config.yml"):
        self.config_file = cfile
        self.config = self.load_config(cfile)
        self.trello_config = self.get_config(["TRELLO"])
        self.cal_config = self.get_config(["CALENDAR"])


    def load_config(self, conf_file="config.yml"):
        file = open(conf_file,"r")
        self.yaml = YAML()
        return self.yaml.load(file)


    def save_cal(self, protocol, url, user, password):
        cal_config['protocol'] = protocol
        cal_config['user'] = user
        cal_config['password'] = password
        cal_config['url'] = url
        file_w = open("config.yml", "w")
        self.yaml.dump(config, file_w)
        file_w.close()
        

    def get_cal_url(self):
        if(cal_config['url'] == None):
            request_calendar()
        else:
            return make_cal_url()

    def make_cal_url(self):
        # url = "https://user:pass@hostname/caldav.php/"
        url = ("%s://%s:%s@%s" % (
            cal_config['protocol'],
            cal_config['user'],
            cal_config['password'],
            cal_config['url']))
        return url


    def get_api_info(self):
        api_key = trello_config['api_key']
        api_secret = trello_config['api_secret']
        return [api_key, api_secret]

    def save_token(self, out):
        write_config(['TRELLO']['oauth_token'], out['oauth_token'])
        write_config(['TRELLO']['oauth_token_secret'], out['oauth_token_secret'])

    def get_client(self):
        return [trello_config['api_key'],
            trello_config['api_secret'],
            trello_config['oauth_token'],
            trello_config['oauth_token_secret']]

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



