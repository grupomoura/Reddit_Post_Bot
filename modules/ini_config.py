"""Carrega configurações do arquivo .ini"""

import configparser

# Lendo o arquivo local config.ini:
config = configparser.ConfigParser()
config.sections()
config.read('config.ini', encoding="UTF-8")
config.sections()

print(config['APP']['reddit_user'])
#Comandos
"""
config.get('DATABASE', 'HOST')
CONFIG['DATABASE'][HOST]
"""