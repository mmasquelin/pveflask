import requests
from ..app import app
from proxmoxer import ProxmoxAPI
from requests.exceptions import ConnectionError, HTTPError, RequestException, Timeout


def get_kvm_hosts(ct_node):
    isc = ProxmoxAPI(host=ct_node, port=app.config["PROXMOX_PORT"],
                     user=app.config["PROXMOX_USERNAME"] + '@' + app.config["PROXMOX_REALM"],
                     password=app.config["PROXMOX_PASSWORD"], verify_ssl=False)
    for node in isc.nodes.get():
        for vm in isc.nodes(node['node']).qemu.get():
            print("{0}. {1} => {2}".format(vm['vmid'], vm['name'], vm['status']))


def get_lxc_hosts(ct_node):
    isc = ProxmoxAPI(host=ct_node, port=app.config["PROXMOX_PORT"],
                     user=app.config["PROXMOX_USERNAME"] + '@' + app.config["PROXMOX_REALM"],
                     password=app.config["PROXMOX_PASSWORD"],
                     verify_ssl=False)

    try:
        for node in isc.nodes.get():
            for vm in isc.nodes(node['node']).lxc.get():
                for vmcfg in isc.nodes(node['node']).lxc(vm['vmid']).config.get():
                    interfaces = []
                    if 'net' in vmcfg:
                        mac = vmcfg
                        ip = isc.nodes(node['node']).lxc(vm['vmid']).config.get()[mac]
                        interfaces.append([mac, ip])
                        print(
                            f'{interfaces} | {node["node"]} - {vm["type"]} - id: {vm["vmid"]} | {vm["name"]} => {vm["status"]}')
    except:
        pass


def get_openvz_hosts(ct_node):
    isc = ProxmoxAPI(host=ct_node, port=app.config["PROXMOX_PORT"],
                     user=app.config["PROXMOX_USERNAME"] + '@' + app.config["PROXMOX_REALM"],
                     password=app.config["PROXMOX_PASSWORD"],
                     verify_ssl=False)
    try:
        for node in isc.nodes.get():
            for vm in isc.nodes(node['node']).openvz.get():
                for vmcfg in isc.nodes(node['node']).openvz(vm['vmid']).config.get():
                    interfaces = []
                    if 'net' in vmcfg:
                        mac = vmcfg
                        ip = isc.nodes(node['node']).openvz(vm['vmid']).config.get()[mac]
                        interfaces.append([mac, ip])
                        print(
                            f'{interfaces} | {node["node"]} - {vm["type"]} - id: {vm["vmid"]} | {vm["name"]} => {vm["status"]}')
    except:
        pass


@app.route('/list', methods=['GET'])
def list_all_vms():
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
                get_kvm_hosts(ct_node)
                get_lxc_hosts(ct_node)
                get_openvz_hosts(ct_node)
                continue
    return "Success"
