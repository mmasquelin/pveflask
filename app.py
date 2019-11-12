from flask import Flask

app = Flask(__name__)
app.config.from_pyfile('config_app.py')

@app.route('/')
@app.route('/index')
def index():
    return '''
    <h1>It works!</h1><br/>
    '''

if __name__ == '__main__':
    app.run()
