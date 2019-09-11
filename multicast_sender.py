import socket

multicast_group = '239.0.0.1'
multicast_port = 8888

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

# default value 1 works
# sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)

for x in range(1, 11):
    test = [x, 2, 1, 3, 0, 0, 0, 0, 0, 0, 0, 0]
    test2 = 'JohnnyDepp'
    test3 = [0, 1]

    data = bytes(test) + bytes(test2, 'utf-8') + bytes(test3)
    sock.sendto(data, (multicast_group, multicast_port))
