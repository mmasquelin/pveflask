import json
import re
import requests
from ..app import app
from proxmoxer import ProxmoxAPI
from requests.exceptions import ConnectionError, HTTPError, RequestException, Timeout


class VM(object):
    '''
    The VM class allows to define a VM with tons of properties
    '''
    name = None
    vm_type = None
    vmid = -1
    node = None
    description = None
    status = "unknown"
    network_info = None

    def __init__(self, name=name, vm_type=vm_type, vmid=vmid, network_info=network_info, status=status, node=node,
                 description=description):
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


class NetworkInterface(object):
    '''
    The NetworkInterface class allows to specify network details for a VM
    '''
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


def get_kvm_hosts(ct_node):
    isc = ProxmoxAPI(host=ct_node, port=app.config["PROXMOX_PORT"],
                     user=app.config["PROXMOX_USERNAME"] + '@' + app.config["PROXMOX_REALM"],
                     password=app.config["PROXMOX_PASSWORD"], verify_ssl=False)
    for node in isc.nodes.get():
        for vm in isc.nodes(node['node']).qemu.get():
            print("{0}. {1} => {2}".format(vm['vmid'], vm['name'], vm['status']))
    return None


def get_lxc_hosts(ct_node):
    isc = ProxmoxAPI(host=ct_node, port=app.config["PROXMOX_PORT"],
                     user=app.config["PROXMOX_USERNAME"] + '@' + app.config["PROXMOX_REALM"],
                     password=app.config["PROXMOX_PASSWORD"],
                     verify_ssl=False)
    lxc_host_details = {}

    try:
        nodes = []
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
                nodes.append({
                    "node": node['node'], "vmid": vm['vmid'], "type": vm['type'], "name": vm['name'],
                    "status": vm['status'], "network_info": pve_iface})
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


@app.route('/list', methods=['GET'])
def list_all_vms(cluster_node):
    print('Selected cluster node is: ' + cluster_node)
    if cluster_node == 'all':
        print('Matches all for %s' % cluster_node)
    isc_details = {}
    ct_nodes_details = []
    nodes = len(app.config["PROXMOX_CLUSTERS"])
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
                lxc_values =  get_lxc_hosts(ct_node)
                if lxc_values:
                    ct_nodes_details.append({"ct_node_name": ct_node, "lxc_details": lxc_values})
                openvz_values = None
                openvz_values = get_openvz_hosts(ct_node)
                if openvz_values:
                    ct_nodes_details.append({"ct_node_name": ct_node, "openvz_details": openvz_values})
                isc_details.update({"status": "Cluster details", "nodes": ct_nodes_details})
                continue
    return json.dumps(isc_details)
