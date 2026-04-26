# config.py - Overall configuration manager. Holds all of the configuration
#             settings for the master controller.

class Config:
    config = None

    def __init__(self, base_config):
        if not Config.config:
            Config.config = base_config 
        else:
            for key in base_config:
                self.set(key, base_config[key])
                

    def get(name):
        try:
            return Config.config[name]

        except KeyError as error:
            return None

    def set(name, val):
        Config.config[name] = val

