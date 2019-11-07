import os
from flask import send_from_directory
from ..app import app


@app.route('/favicon.ico')
@app.route('/apple-touch-icon.png')
@app.route('/apple-touch-ipad.png')
@app.route('/apple-touch-iphone.png')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'images/favicon.png', mimetype='image/png')
