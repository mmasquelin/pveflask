class NetworkService(object):
    '''
    The NetworkService class contains parameters and methods to describe a network service and allow to instantiate
     a network service object.
    '''
    name = None
    port = -1
    transport_protocol = None
    description = None

    def __init__(self, name=name, port=port, transport_protocol=transport_protocol, description=description):
        self.name = name
        self.port = port
        self.transport_protocol = transport_protocol
        self.description = description

    def __repr__(self):
        return {
            'name': self.name, 'port': self.port, 'transport_protocol': self.transport_protocol,
            'description': self.description}

    def __str__(self):
        return 'NetworkService(name=' + self.name + ', port=' + str(
            self.port) + ', proto=' + self.transport_protocol + ')'

    def __eq__(self, service):
        """
        This method tests if two network services object are similar
        :param service: a NetworkService object
        :return: True or False, depends on kind of NetworkService
        """
        return self.port == service.port and self.transport_protocol == service.transport_protocol

    def is_ftp(self):
        return (self.port == 21 and self.transport_protocol == "tcp") or (self.port == 21 and self.transport_protocol == "udp")

    def is_ssh(self):
        return (self.port == 22 and self.transport_protocol == "tcp") or (self.port == 22 and self.transport_protocol == "udp") or (self.port == 22 and self.transport_protocol == "sctp")

    def is_telnet(self):
        return (self.port == 23 and self.transport_protocol == "tcp") or (self.port == 23 and self.transport_protocol == "udp")

    def is_smtp(self):
        return (self.port == 25 and self.transport_protocol == "tcp") or (self.port == 25 and self.transport_protocol == "udp")

    def is_http(self):
        return self.port == 80 and self.transport_protocol == "tcp"

    def is_sunrpc(self):
        return (self.port == 111 and self.transport_protocol == "tcp") or (self.port == 111 and self.transport_protocol == "udp")

    def is_imap(self):
        return (self.port == 143 and self.transport_protocol == "tcp") or (self.port == 143 and self.transport_protocol == "udp")

    def is_ldap(self):
        return (self.port == 389 and self.transport_protocol == "tcp") or (self.port == 389 and self.transport_protocol == "udp")

    def is_https(self):
        return self.port == 443 and self.transport_protocol == "tcp"

    def is_rndc(self):
        return self.port == 953 and self.transport_protocol == "tcp"

    def is_sieve(self):
        return (self.port == 4190 and self.transport_protocol == "tcp")

    def is_sunproxyadmin(self):
        return (self.port == 8081 and self.transport_protocol == "tcp") or (self.port == 8081 and self.transport_protocol == "udp")