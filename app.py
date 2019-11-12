from flask import Flask

app = Flask(__name__)
app.config.from_pyfile('config_app.py')

if __name__ == '__main__':
    app.run()
