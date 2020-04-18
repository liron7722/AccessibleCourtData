import socket

DOMAIN = "localhost"
PORT = 9200


def is_connected(hostname=DOMAIN, port=PORT):
    try:
        # see if we can resolve the host name -- tells us if there is
        # a DNS listening
        host = socket.gethostbyname(hostname)
        # connect to the host -- tells us if the host is actually
        # reachable
        s = socket.create_connection((host, port), 10)
        s.close()
        return True
    except:
        return False

#
# if __name__ == '__main__':
#     print(is_connected())
