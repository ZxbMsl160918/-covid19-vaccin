import configparser
import os


class Config(object):
    def __init__(self, config_file='config/config.ini'):
        self._path = os.path.join(os.getcwd(), config_file)
        if not os.path.exists(self._path):
            raise FileNotFoundError("找不到文件: config.ini")
        self._config = configparser.ConfigParser()
        self._config.read(self._path, encoding='utf-8-sig')

    def get(self, section, option):
        """
        获取 :section 配置下的配置项
        :param section: section 名
        :param option: key 名
        :return:
        """
        return self._config.get(section, option)

    def getConfigSection(self, option):
        """
        获取 [config] 配置下的配置项
        :param option: key 名
        :return:
        """
        return self._config.get("config", option)


global_config = Config()
