import configparser
import os

config = configparser.ConfigParser()
PROJECT_PATH = ('global_config.ini', 'project', 'project_path')
IS_UPDATE = ('global_config.ini', 'project', 'is_update')


def getValue(fileName, sections, key):
    path = getPath(fileName)
    config.read(path)
    return config.get(sections, key)


def getPath(fileName):
    return os.path.dirname(os.path.abspath(__file__)) + r"\data\{}".format(fileName)


def setValue(fileName, sections, key, value):
    path = getPath(fileName)
    config.read(path)
    config.set(sections, key, value)
    with open(path, 'w') as f:
        config.write(f)


def getBoolean(fileName, sections, key):
    path = getPath(fileName)
    config.read(path)
    return config.getboolean(sections, key)
