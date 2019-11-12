import os
from flask import send_from_directory
from ..app import app


@app.route('/favicon.ico')
@app.route('/apple-touch-icon.png')
@app.route('/apple-touch-ipad.png')
@app.route('/apple-touch-iphone.png')
def favicon():
    '''
    This function allows to avoid 404 errors complains while browsing the app with a modern web-browser.
    :return: Media favicon full path location
    '''
    return send_from_directory(os.path.join(app.root_path, 'static'), 'images/favicon.png', mimetype='image/png')
