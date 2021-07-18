import socket

'''
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('127.0.0.1', 9999))

print(s.recv(1024).decode('utf-8'))
# for data in [b'Michael', b'Tracy', b'Sarah']: 
#     s.send(data)
#     print(s.recv(1024).decode('utf-8'))
s.send(b'me')
# if send a message but didn't receive, an error happens (TCP?)
print(s.recv(1024).decode('utf-8'))
s.send(b'exit')
s.close()
'''

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
for data in [b'Michael', b'Tracy', b'Sarah']:
    # 发送数据:
    s.sendto(data, ('127.0.0.1', 9999))
    # 接收数据:
    print(s.recv(1024).decode('utf-8'))
s.close()