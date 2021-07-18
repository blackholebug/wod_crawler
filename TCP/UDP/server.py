import socket
import threading
import time

"""
# start a socket with IPV4, TCP
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# bind to ip address and port to listen
s.bind(('127.0.0.1', 9999))
# start to listen to 5 connections
s.listen(5)
print('Waiting for connection')

# 
def tcplink(sock, addr): 
    print('Accepting new connection form %s:%s ...' % addr)
    sock.send(b'Welcome!')
    while True: 
        # receive 1024 byte at most
        data = sock.recv(1024)
        time.sleep(1)
        if not data or data.decode('utf-8') == 'exit':
            break
        sock.send(('Hello, %s' % data.decode('utf-8')).encode('utf-8'))
    sock.close()
    print('Connection from %s:%s is closed' % addr)


while True: 
    # 
    sock, addr = s.accept()
    t = threading.Thread(target=tcplink, args=(sock, addr))
    t.start()
"""

# start a socket with UDP
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('127.0.0.1', 9999))
print('Receiving data on port 9999...')

while True: 
    data, addr = s.recvfrom(1024)
    print('Receiving data from %s:%s.' % addr)
    s.sendto(b'Hello, %s' % data, addr)