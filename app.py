import logging
from flask import Flask


logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_pyfile('config_app.py')

if __name__ == '__main__':
    app.run()
