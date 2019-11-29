from ..app import app
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    '''
    The LoginForm FlaskForm contains credentials
    :username arg: The arg is used to store the user login input
    :type arg: str
    :password arg: The arg is used to store the password input
    :type arg: str
    '''
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')


class ProxmoxNode(FlaskForm):
    '''
    The Proxmox FlaskForm contains lots of PVE clusters
    '''
    # all_nodes = [('none', 'None')]
    all_nodes = []
    for node in app.config['PROXMOX_CLUSTERS']:
        node = ('' + node.partition('.')[0] + '','' + node + '')
        all_nodes.append(node)
    if app.config['PROXMOX_CLUSTERS']:
        all_nodes.append(('all', 'All clusters'))
    node = SelectField('Nodes', choices=all_nodes)
    submit = SubmitField('Send')


class ProxmoxCluster(FlaskForm):
    '''
        The Proxmox FlaskForm contains lots of PVE clusters
        '''
    # all_nodes = [('none', 'None')]
    all_nodes = []
    for node in app.config['PROXMOX_CLUSTERS']:
        node = ('' + node.partition('.')[0] + '', '' + node + '')
        all_nodes.append(node)
    if app.config['PROXMOX_CLUSTERS']:
        all_nodes.append(('all', 'All clusters'))
    node = SelectField('Nodes', choices=all_nodes)
    submit = SubmitField('Send')


class VirtualMachine(object):
    pass