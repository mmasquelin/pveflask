from flask import render_template, flash, redirect, url_for
from .gui import LoginForm, ProxmoxNode
from ..app import app


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for user {}, remember_me={}'.format(
            form.username.data, form.remember_me.data))
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)

@app.route('/view/nodes', methods=['GET', 'POST'])
def viewNodes():
    form = ProxmoxNode()
    #if form.validate_on_submit():
    #    return render_template('nodes.html', title='Select node', form=form)
    return render_template('nodes.html', title='Select node', form=form)