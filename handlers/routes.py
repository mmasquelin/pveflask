import os
from fabric import Connection
from flask import flash, render_template, redirect, send_from_directory, url_for
from .gui import LoginForm, ProxmoxNode
from .proxmox import list_all_vms
from ..app import app

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Main')


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


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for user {}, remember_me={}'.format(
            form.username.data, form.remember_me.data))
        return redirect(url_for('view_nodes'))
    return render_template('login.html', title='Sign In', form=form)


@app.route('/view/clusters', methods=['GET'])
def get_cluster_details():
    pass


@app.route('/view/nodes', methods=['GET', 'POST'])
def view_nodes():
    form = ProxmoxNode()
    if form.validate_on_submit():
        # print(form.node.data)
        return render_template('details.html', title='Selected node(s)', datas=list_all_vms(form.node.data))
        # return render_template('details.html', title='Selected node(s)', datas=list_all_vms())
    return render_template('nodes.html', title='Select node', form=form)


@app.route('/view/ssh', methods=['GET', 'POST'])
def connect_to_openssh():
    client = Connection(host=app.config['SSH_IP'], user=app.config['SSH_USERNAME'], port=app.config['SSH_PORT'], connect_kwargs={"password": app.config['SSH_PASSWORD']})
    result = client.run('uname -a')
    return result.stdout.strip()