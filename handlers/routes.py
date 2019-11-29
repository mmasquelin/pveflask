import os
import json
from fabric import Connection
from flask import flash, render_template, redirect, send_from_directory, url_for, json, request
from .gui import LoginForm, ProxmoxNode, ProxmoxCluster
from .common import is_word_in_text
from .logging import get_logger
from .proxmox import NetworkInterface, VM, list_all_vms, get_lxc_hosts, view_lxc_hosts
from .services import NetworkService
from ..app import app

logging = get_logger(__package__)


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


@app.route('/test', methods=['GET'])
def test():
    service = NetworkService("http",80,"tcp","HTTP (HyperText Transfer Protocol)")
    try:
        details = "name=eth1,bridge=vmbr3,hwaddr=1E:8C:0E:6B:04:9F,ip=dhcp,type=veth"
        interface = NetworkInterface().set_interface_details("test","net0", details)
        print(interface)
    except ValueError as v:
        logging.error('Erreur')
    return service.__str__()


@app.route('/view/clusters', methods=['GET', 'POST'])
def view_clusters():
    form = ProxmoxCluster()
    if form.validate_on_submit():
        return render_template('cluster_details.html', title='Selected node(s)', datas=json.loads(list_all_vms()))
    return render_template('clusters.html', title='Select node', form=form)


@app.route('/view/node/<node_name>', methods=['GET'])
def view_node(node_name):
    logging.debug(node_name)
    return render_template('node_details.html', title='Node content details', node_name=node_name, datas=json.loads(view_lxc_hosts(node_name)))

@app.route('/view/node/kernel_info', methods=['GET', 'POST'])
def view_node_kernel():
    client = Connection(host=app.config['SSH_IP'], user=app.config['SSH_USERNAME'], port=app.config['SSH_PORT'],
                        connect_kwargs={"password": app.config['SSH_PASSWORD']})
    result = client.run('uname -a')
    return result.stdout.strip()


@app.route('/view/node/tcp_connections', methods=['GET', 'POST'])
def view_node_tcp_conn():
    tcp_conn = {}
    tcp_conn_values = []
    client = Connection(host=app.config['SSH_IP'], user=app.config['SSH_USERNAME'], port=app.config['SSH_PORT'],
                        connect_kwargs={"password": app.config['SSH_PASSWORD']})
    # r prefix is used to allow raw commands and avoid complex escaping sequences
    command = r'''find /proc/ 2>/dev/null | grep tcp | grep -v task | grep -v sys/net | xargs grep -v rem_address 2>/dev/null | awk '{x=strtonum("0x"substr($3,index($3,":")-2,2)); y=strtonum("0x"substr($4,index($4,":")-2,2)); for (i=5; i>0; i-=2) x = x"."strtonum("0x"substr($3,i,2)); for (i=5; i>0; i-=2) y = y"."strtonum("0x"substr($4,i,2))}{printf ("%s\t:%s\t ----> \t %s\t:%s\t%s\n",x,strtonum("0x"substr($3,index($3,":")+1,4)),y,strtonum("0x"substr($4,index($4,":")+1,4)),$1)}' | sort | uniq --check-chars=25'''
    result = client.run(command)
    try:
        for service in result.stdout.split("\n"):
            try:
                tcp_conn_values.append({
                                           'ip_source': service.split("\t")[0], 'port_source': int(service.split("\t")[1].replace(':','')),
                                           'ip_destination': service.split("\t")[3],
                                           'port_destination': int(service.split("\t")[4].replace(':',''))})
            except:
                pass
    except:
        pass
    tcp_conn.update({"status": "TCP connections details", "values": tcp_conn_values})
    return json.dumps(tcp_conn)


@app.route('/view/node/udp_connections', methods=['GET'])
def view_node_udp_conn():
    udp_conn = {}
    udp_conn_values = []
    client = Connection(host=app.config['SSH_IP'], user=app.config['SSH_USERNAME'], port=app.config['SSH_PORT'],
                        connect_kwargs={"password": app.config['SSH_PASSWORD']})
    command = r'''find /proc/ 2>/dev/null | grep udp | grep -v task | grep -v sys/net | xargs grep -v rem_address 2>/dev/null | awk '{x=strtonum("0x"substr($3,index($3,":")-2,2)); y=strtonum("0x"substr($4,index($4,":")-2,2)); for (i=5; i>0; i-=2) x = x"."strtonum("0x"substr($3,i,2)); for (i=5; i>0; i-=2) y = y"."strtonum("0x"substr($4,i,2))}{printf ("%s\t:%s\t ----> \t %s\t:%s\t%s\n",x,strtonum("0x"substr($3,index($3,":")+1,4)),y,strtonum("0x"substr($4,index($4,":")+1,4)),$1)}' | sort | uniq --check-chars=25'''
    result = client.run(command)
    try:
        for service in result.stdout.split("\n"):
            try:
                udp_conn_values.append({
                                           'ip_source': service.split("\t")[0], 'port_source': int(service.split("\t")[1].replace(':','')),
                                           'ip_destination': service.split("\t")[3],
                                           'port_destination': int(service.split("\t")[4].replace(':',''))})
            except:
                pass
    except:
        pass
    udp_conn.update({"status": "TCP connections details", "values": udp_conn_values})
    return json.dumps(udp_conn)


@app.route('/view/node/arp_table', methods=['GET'])
def view_arp_results():
    arp = {}
    arp_table_values = []
    client = Connection(host=app.config['SSH_IP'], user=app.config['SSH_USERNAME'], port=app.config['SSH_PORT'],
                        connect_kwargs={"password": app.config['SSH_PASSWORD']})
    command = """for i in $(route -n | awk 'NR > 2 && !seen[$1$2]++  {print $8}');do arp-scan -I $i -l --quiet | head -n -3 | tail -n +3 ; done | awk '!seen[$1$2]++ { print $1"="$2;}'"""

    result = client.run(command)
    try:
        for line in result.stdout.split("\n"):
            try:
                arp_table_values.append({'ip': line.split("=")[0].upper(), 'hwaddr': str(line.split("=")[1].upper())})
            except:
                pass
    except:
        pass
    arp.update({"status": "ARP table details", "values": arp_table_values})
    return arp
