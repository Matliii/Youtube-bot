from configparser import ConfigParser

file = 'config.ini'
config = ConfigParser()
config.read(file)

CLIENT_ID = config['OAuth']['Client_id']
ClientSecret = config['OAuth']['Client_secret']

Name = config['setup']['Username']
Shuffle = config.getint('setup', 'SHUFFLE_NUMBER')


