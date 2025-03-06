# -*- coding: utf-8 -*-
import time
from loguru import logger
import os

basedir = '/var/log'
log_path = os.path.join(basedir, 'keyvault-sdk')
if not os.path.exists(log_path):
    os.mkdir(log_path)
path = os.path.join(log_path, f'sdk-decrypt-{time.strftime("%Y-%m-%d")}.log')
logger.add(path, rotation='10 MB', retention="7 days", level='INFO', format='{message}')
