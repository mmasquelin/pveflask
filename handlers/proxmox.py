import json
import re
import requests
import socket
from tqdm import tqdm
from .common import is_word_in_text, pp_json
from .logging import get_logger
from flask import request, jsonify, make_response
from flask_json import json_response
from ..app import app
from proxmoxer import ProxmoxAPI
from requests.exceptions import ConnectionError, HTTPError, RequestException, Timeout


logging = get_logger(__package__)


class PVECluster(object):
    cluster_name = None
    cluster_nodes = None

    def __init__(self, cluster_name=cluster_name, cluster_nodes=cluster_nodes):
        if cluster_nodes is None:
            cluster_nodes = []
        self.cluster_name=cluster_name
        self.cluster_nodes=cluster_nodes

    def __str__(self):
        return 'PVE_Cluster(cluster_name=' + str(self.cluster_name) + ')'

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def get_cluster_nodes(self, ct_node):
        ct_node_url = app.config["PROXMOX_APP_PROTOCOL"] + ct_node + ':' + str(
            app.config["PROXMOX_PORT"]) + '/'
        try:
            r = requests.get(ct_node_url, timeout=5, verify=app.config["PROXMOX_SSL_VERIFY"])
            # If the response was successful, no exception will be raised
            r.raise_for_status()
            isc = ProxmoxAPI(host=ct_node, port=app.config["PROXMOX_PORT"],
                             user=app.config["PROXMOX_USERNAME"] + '@' + app.config["PROXMOX_REALM"],
                             password=app.config["PROXMOX_PASSWORD"],
                             verify_ssl=False)
            cluster = PVECluster(ct_node)
            for node_details in isc.nodes.get():
                machine = PVENode(node_details['node'], socket.gethostbyname(node_details['node'] + '.' + app.config["PROXMOX_DOMAIN_NAME"]), 'Aucune')
                cluster.cluster_nodes.append(json.loads(machine.to_json()))
        except ConnectionError as connection_err:
            print(f'Connection error occurred: {connection_err}')
            return "Error"
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
            return "Error"
        except Timeout as timeout_err:
            print(f'Timeout error occurred: {timeout_err}')
            return "Error"
        except RequestException as request_err:
            print(f'Request error occurred: {request_err}')
            return "Error"
        except Exception as err:
            print(f'Other error occurred: {err}')
            return "Error"
        return cluster.to_json()

class PVENode(object):
    """
    The PVENode class allow to describe a PVE node
    """
    node_name = None
    ipv4 = "127.0.0.1/32"
    description = None
    vms = []

    def __init__(self, node_name=node_name, ipv4=ipv4, description=description, parent=None, vms=vms):
        """
        Initialize the object PVE cluster
        :param name:
        :param ipv4:
        :param description:
        """
        self.node_name = node_name
        self.ipv4 = ipv4
        self.description = description
        self.vms = vms

    def __str__(self):
        return 'PVE_Node(node_name=' + str(self.node_name) + ', ip_address=' + str(self.ipv4) + ')'

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)


class VM(object):
    """
    The VM class allows to define a VM with tons of properties
    """
    name = None
    vm_type = None
    vmid = -1
    node = None
    description = None
    status = "unknown"
    network_info = None

    def __init__(self, name=name, vm_type=vm_type, vmid=vmid, network_info=network_info, status=status, node=node,
                 description=description):
        '''Initialize the object VM'''
        self.name = name
        self.vm_type = vm_type
        self.vmid = vmid
        self.network_info = network_info
        self.status = status
        self.node = node
        self.description = description

    def __str__(self):
        return 'VM(node=' + str(self.node) + ', vmid=' + str(self.vmid) + ', name=' + str(
            self.name) + ', status=' + self.status + ')'

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)


class NetworkInterface(object):
    """
    The NetworkInterface class allows to specify network details for a VM
    """
    name = "net0"
    internal_name = "eth0"
    bridge = "vmbr0"
    hwaddr = "FF:FF:FF:FF:FF:FF"
    ip = "dhcp"
    type = "veth"
    vm = None
    description = "Primary network interface"

    def __init__(self, name=name, internal_name=internal_name, bridge=bridge, hwaddr=hwaddr, ip=ip, type=type, vm=vm,
                 description=description):
        self.name = name
        self.internal_name = internal_name
        self.bridge = bridge
        self.hwaddr = hwaddr
        self.ip = ip
        self.type = type
        self.vm = vm
        self.description = description

    def __str__(self):
        return 'NetworkInterface(name=' + self.internal_name + ', ip=' + self.ip + ', hwaddr=' + self.hwaddr + ')'

    def set_interface_details(self, pve_vm, pve_iface_name, pve_iface_details):
        cur_iface_details = dict(x.split('=') for x in pve_iface_details.split(','))
        return NetworkInterface(internal_name=pve_iface_name, name=str(cur_iface_details['name']),
                                ip=str(cur_iface_details['ip']), hwaddr=str(cur_iface_details['hwaddr']),
                                bridge=str(cur_iface_details['bridge']), type=str(cur_iface_details['type']), vm=pve_vm,
                                description=str(None), )

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)


def get_kvm_hosts(ct_node):
    isc = ProxmoxAPI(host=ct_node, port=app.config["PROXMOX_PORT"],
                     user=app.config["PROXMOX_USERNAME"] + '@' + app.config["PROXMOX_REALM"],
                     password=app.config["PROXMOX_PASSWORD"], verify_ssl=False)
    for node in isc.nodes.get():
        for vm in isc.nodes(node['node']).qemu.get():
            print("{0}. {1} => {2}".format(vm['vmid'], vm['name'], vm['status']))
    return None


def view_lxc_hosts(ct_node):
    try:
        my_node = PVENode(node_name=ct_node).__dict__
    except:
        pass
    logging.debug('Selected node is: ' + ct_node)
    isc = ProxmoxAPI(host=ct_node, port=app.config["PROXMOX_PORT"],
                     user=app.config["PROXMOX_USERNAME"] + '@' + app.config["PROXMOX_REALM"],
                     password=app.config["PROXMOX_PASSWORD"],
                     verify_ssl=False)
    try:
        for vm in isc.nodes(ct_node).lxc.get():
            my_node['vms'].append(VM(name=vm['name'], vm_type=vm['type'], vmid=vm['vmid'], status=vm['status'], node=ct_node).__dict__)
    except:
        pass
    try:
        for vm in isc.nodes(ct_node).openvz.get():
            my_node['vms'].append(VM(name=vm['name'], vm_type=vm['type'], vmid=vm['vmid'], status=vm['status'], node=ct_node).__dict__)
    except:
        pass
    try:
        for vm in isc.nodes(ct_node).qemu.get():
            my_node['vms'].append(VM(name=vm['name'], vm_type='kvm', vmid=vm['vmid'], status=vm['status'], node=ct_node).__dict__)
    except:
        pass
    return json.dumps(my_node)

def get_lxc_hosts(ct_node):
    logging.debug('Calling get_lxc_host method for ' + ct_node)
    isc = ProxmoxAPI(host=ct_node, port=app.config["PROXMOX_PORT"],
                     user=app.config["PROXMOX_USERNAME"] + '@' + app.config["PROXMOX_REALM"],
                     password=app.config["PROXMOX_PASSWORD"],
                     verify_ssl=False)
    lxc_host_details = {}

    try:
        if ct_node == 'all':
            nodes = []
        else:
            nodes = ct_node
        for node in isc.nodes.get():
            for vm in isc.nodes(node['node']).lxc.get():
                pve_iface = []
                for vmcfg in isc.nodes(node['node']).lxc(vm['vmid']).config.get():
                    if 'net' in vmcfg:
                        pve_iface_name = vmcfg
                        pve_iface_details = isc.nodes(node['node']).lxc(vm['vmid']).config.get()[pve_iface_name]
                        pve_iface.append({
                            "pve_iface_name": pve_iface_name,
                            "pve_iface_details": pve_iface_details
                        })
                        interface = NetworkInterface().set_interface_details(
                            pve_vm=isc.nodes(node['node']).lxc(vm['name']), pve_iface_name=vmcfg,
                            pve_iface_details=isc.nodes(node['node']).lxc(vm['vmid']).config.get()[pve_iface_name])
                        # print(interface.to_json())
                        print({"node": str(node['node']), "vmid": vm['vmid'], "type": vm['type'], "name": vm['name'],"status": vm['status'], "network_info": pve_iface})
                nodes.append({
                    "node": node['node'], "vmid": vm['vmid'], "type": vm['type'], "name": vm['name'],
                    "status": vm['status'], "network_info": pve_iface})
        # Display the dict 'nodes' content
        for n in nodes:
            print(n)
            for v in nodes[x]:
                print(v, ':', nodes[x][y])
        lxc_host_details.update({"status": "Host details", "vms": nodes})
        return lxc_host_details
    except:
        pass


def get_openvz_hosts(ct_node):
    isc = ProxmoxAPI(host=ct_node, port=app.config["PROXMOX_PORT"],
                     user=app.config["PROXMOX_USERNAME"] + '@' + app.config["PROXMOX_REALM"],
                     password=app.config["PROXMOX_PASSWORD"],
                     verify_ssl=False)
    openvz_host_details = {}

    try:
        nodes = []
        for node in isc.nodes.get():
            for vm in isc.nodes(node['node']).openvz.get():
                pve_iface = []
                for vmcfg in isc.nodes(node['node']).openvz(vm['vmid']).config.get():
                    if 'net' in vmcfg:
                        pve_iface_name = vmcfg
                        pve_iface_details = isc.nodes(node['node']).openvz(vm['vmid']).config.get()[pve_iface_name]
                        pve_iface.append({
                            "pve_iface_name": pve_iface_name,
                            "pve_iface_details": pve_iface_details
                        })
                nodes.append({
                    "node": node['node'], "vmid": vm['vmid'], "type": vm['type'], "name": vm['name'],
                    "status": vm['status'], "network_info": pve_iface})
        openvz_host_details.update({"status": "Host details", "vms": nodes})
        return openvz_host_details
    except:
        pass


# @app.route('/list', methods=['POST'])
def list_all_vms():
    clusters_list = []
    all_clusters =[]
    if request.method == 'POST':
        if str(request.form['node']) is not None:
            logging.debug('Selected cluster is: ' + str(request.form['node']))
            logging.debug('Cluster list is: ' + str(app.config["PROXMOX_CLUSTERS"]))
            if app.config["PROXMOX_CLUSTERS"] is not None:
                for node in app.config["PROXMOX_CLUSTERS"]:
                    if is_word_in_text(str(request.form['node']), str(node)):
                        logging.debug('Trying to display cluster ' + str(node) + ' details...')
                        all_clusters = PVECluster().get_cluster_nodes(str(node))
                    if str(request.form['node']) == "all":
                        # clusters_list.append(json.loads(PVECluster().get_cluster_nodes(str(node))))
                        # all_clusters = json.dumps({"data": clusters_list}, default=lambda o: o.__dict__, sort_keys=True, indent=4)
                        clusters_list = []
                        logging.debug('Trying to display cluster ' + str(node) + ' details...')
                        clusters_list = (PVECluster().get_cluster_nodes(str(node)))
                        all_clusters = clusters_list
                    if str(request.form['node']) is None:
                        all_clusters = None
    # res = make_response(jsonify({"data": all_clusters}), 200)
    # print(res)
    # return res
    return all_clusters

@app.route('/liste', methods=['GET', 'POST'])
def liste_all_vms(cluster_node):
    print('Selected cluster node is: ' + cluster_node)
    if cluster_node == 'all':
        print('Matches all for %s' % cluster_node)
    isc_details = {}
    ct_nodes_details = []
    nodes = len(app.config["PROXMOX_CLUSTERS"])
    logging.debug('Cluster nodes:' + str(nodes))
    while 1:
        if nodes == 0:
            break
        else:
            ct_node = app.config["PROXMOX_CLUSTERS"].pop()
            ct_node_url = app.config["PROXMOX_APP_PROTOCOL"] + ct_node + ':' + str(app.config["PROXMOX_PORT"]) + '/'
            try:
                r = requests.get(ct_node_url, timeout=5, verify=app.config["PROXMOX_SSL_VERIFY"])
                # If the response was successful, no exception will be raised
                r.raise_for_status()
            except ConnectionError as connection_err:
                print(f'Connection error occurred: {connection_err}')
                return "Error"
            except HTTPError as http_err:
                print(f'HTTP error occurred: {http_err}')
                return "Error"
            except Timeout as timeout_err:
                print(f'Timeout error occurred: {timeout_err}')
                return "Error"
            except RequestException as request_err:
                print(f'Request error occurred: {request_err}')
                return "Error"
            except Exception as err:
                print(f'Other error occurred: {err}')
                return "Error"
            else:
                nodes -= 1
                kvm_values = None
                kvm_values = get_kvm_hosts(ct_node)
                if kvm_values:
                    ct_nodes_details.append({"ct_node_name": ct_node, "kvm_details": kvm_values})
                lxc_values = None
                lxc_values = get_lxc_hosts(ct_node)
                if lxc_values:
                    ct_nodes_details.append({"ct_node_name": ct_node, "lxc_details": lxc_values})
                openvz_values = None
                openvz_values = get_openvz_hosts(ct_node)
                if openvz_values:
                    ct_nodes_details.append({"ct_node_name": ct_node, "openvz_details": openvz_values})
                isc_details.update({"status": "Cluster details", "nodes": ct_nodes_details})
                continue
    return json.dumps(isc_details)
