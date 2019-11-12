# pveflask
Proxmox Virtual Environment companion, written with Flask.

## Setup

See 'requirements.txt' file for dependencies.

## Webapp configuration

Configuration could be achieved with a file *'config_app.py'*. It has to be located in the app main folder. 

Here is a sample *'config.app.py'* file output :
```
SECRET_KEY = 'my-super-secret-key'

PROXMOX_CLUSTERS = ['mycluster1.priv.mydomain', 'mycluster2.myotherdomain']
PROXMOX_SSL_VERIFY = False
PROXMOX_APP_PROTOCOL = "https://"
PROXMOX_PORT = 8006
PROXMOX_USERNAME = "john.doe"
PROXMOX_PASSWORD = "passw0rd"
PROXMOX_REALM = "myrealm"
```
