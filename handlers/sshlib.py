import logging
import paramiko
import socket

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class SSHClient(object):
    def __init__(self, ssh_host, ssh_port, ssh_username, ssh_password):
        self.connection = self.connect(ssh_host, ssh_port, ssh_username, ssh_password)

    def connect(self, ssh_host, ssh_port, ssh_username, ssh_password):
        """
        Initiates an SSH connection to the specified hostname
        :param ssh_host: SSH hostname (IP or host + fqdn)
        :param ssh_port: SSH port number
        :param ssh_username: SSH username
        :param ssh_password: SSH password
        :return: SSHObject (connection link)
        """

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        print('Hostname is: ' + socket.gethostbyname(ssh_host))

        try:
            client.connect(socket.gethostbyname(ssh_host), port=22, username=ssh_username, password=ssh_password)
            logger.info("Connection created (host = {}, username = {}, password = *****)".format(ssh_host, ssh_username))
        except paramiko.AuthenticationException:
            logger.error("Authentication error")
        except paramiko.SSHException as sshException:
            logger.error("Could not establish SSH connection: %s" % sshException)
        except socket.timeout as e:
            logger.error("Communication problem: %s" % e)
        except ValueError:
            logger.error("Connection failed")

        return client

    def execute(self, command):
        """
        Executes a command via SSH and returns results on stdout
        :param command: A string, the desired command output
        :return: An output (stdout stream)
        """
        logger.debug("Executing command on stdout:\n\t{}".format(command.strip()))
        return self.connection.exec_command(command.strip())

    def close(self):
        self.connection.close()