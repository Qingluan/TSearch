from mroylib.config import Config
import os

CONF_PATH = os.path.expanduser("~/.config/searcher.ini")
configuration = None
if os.path.exists(CONF_PATH):
    configuration = Config(file=CONF_PATH)
else:
    configuration = Config(file=CONF_PATH)

