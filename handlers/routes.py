from flask import render_template, flash, redirect, url_for
from .gui import LoginForm, ProxmoxNode
from .proxmox import list_all_vms
from ..app import app


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Main')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for user {}, remember_me={}'.format(
            form.username.data, form.remember_me.data))
        return redirect(url_for('view_nodes'))
    return render_template('login.html', title='Sign In', form=form)


@app.route('/view/nodes', methods=['GET', 'POST'])
def view_nodes():
    form = ProxmoxNode()
    if form.validate_on_submit():
        return render_template('details.html', title='Selected node(s)', datas=list_all_vms())
    return render_template('nodes.html', title='Select node', form=form)
