import ConfigParser
import logging

class Config:
    def __init__(self, configFile):
        self.Config = ConfigParser.ConfigParser()
        self.Config.read(configFile)
        logging.info(self.Config.sections())

    def ConfigSectionMap(self, section):
        dict1 = {}
        options = self.Config.options(section)
        for option in options:
            try:
                dict1[option] = self.Config.get(section, option)
                if dict1[option] == -1:
                    logger.debug("skip: %s" % option)
            except:
                logging.error("exception on %s!" % option)
                dict1[option] = None
        return dict1
