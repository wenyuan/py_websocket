#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ref: @https://www.jianshu.com/p/3f42172f582b

import hashlib
import socket
import base64
from threading import Thread

global clients
clients = {}


# 通知客户端
def notify(message):
    for connection in clients.values():
        connection.send('%c%c%s' % (0x81, len(message), message))


# 客户端处理线程
class WebSocketThread(Thread):
    def __init__(self, connection, username):
        super(WebSocketThread, self).__init__()
        self.connection = connection
        self.username = username

    def run(self):
        print('new websocket client joined!')
        # 服务端响应报文
        # @https://www.cnblogs.com/JetpropelledSnake/p/9033064.html
        data = self.connection.recv(1024)
        headers = self.parse_headers(data)
        if 'Sec-WebSocket-Key' not in headers :
            print('This socket is not websocket, client close')
            self.connection.close()
            return
        magic_key = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
        token = self.generate_token(headers['Sec-WebSocket-Key'], magic_key)

        response = 'HTTP/1.1 101 WebSocket Protocol Hybi-10\r\n' \
                   'Connection: Upgrade\r\n' \
                   'Upgrade: WebSocket\r\n' \
                   'Sec-WebSocket-Accept: {token}\r\n' \
                   'WebSocket-Protocol: chat\r\n\r\n'.format(token=token)
        # self.connection.send(response)
        self.connection.send('\
        HTTP/1.1 101 WebSocket Protocol Hybi-10\r\n\
        Upgrade: WebSocket\r\n\
        Connection: Upgrade\r\n\
        Sec-WebSocket-Accept: %s\r\n\r\n' % token)

        # 进行通信
        while True:
            try:
                data = self.connection.recv(1024)
            except socket.error as e:
                print('unexpected error: ', e)
                clients.pop(self.username)
                break
            data = self.parse_data(data)
            if len(data) == 0:
                continue
            # self.conn.send(data)
            message = self.username + ": " + data
            notify(message)

    def parse_data(self, data):
        msg_len = data[1] & 127    # 数据载荷的长度
        if msg_len == 126:
            mask = data[4:8]       # Mask掩码
            content = data[8:]     # 消息内容
        elif msg_len == 127:
            mask = data[10:14]
            content = data[14:]
        else:
            mask = data[2:6]
            content = data[6:]
        raw_str = ''    # 解码后的内容
        for i, d in enumerate(content):
            raw_str += chr(d ^ mask[i % 4])
        return raw_str



        # v = ord(msg[1]) & 0x7f
        # if v == 0x7e:
        #     p = 4
        # elif v == 0x7f:
        #     p = 10
        # else:
        #     p = 2
        # mask = msg[p:p + 4]
        # data = msg[p + 4:]
        # return ''.join([chr(ord(v) ^ ord(mask[k % 4])) for k, v in enumerate(data)])

    def parse_headers(self, data):
        headers_dict = {}
        headers, _ = data.split('\r\n\r\n', 1)
        for line in headers.split('\r\n')[1:]:
            key, value = line.split(': ', 1)
            headers_dict[key] = value
        headers_dict['data'] = _
        return headers_dict

    def generate_token(self, sec_key, magic_key):
        key = sec_key + magic_key
        return base64.b64encode(hashlib.sha1(key).digest())


# 服务端
class WebSocketServer(object):
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

    def start(self):
        # 创建 tcp socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 设置socket.close()后马上释放该端口,否则默认会经过一个TIME_WAIT
        # @http://www.360doc.com/content/12/0321/14/6312609_196283700.shtml
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind((self.ip, self.port))
            sock.listen(5)
        except Exception as e:
            print('server error!')
            print(e)
        print('websocket server running...')
        # 等待访问
        while True:
            connection, address  = sock.accept()  # 此时会进入waiting状态
            try:
                username = "ID" + str(address [1])
                thread = WebSocketThread(connection, username)
                thread.start()
                clients[username] = connection
            except socket.timeout:
                print('websocket connection timeout!')


if __name__ == '__main__':
    websocket_server = WebSocketServer('127.0.0.1', 9000)
    websocket_server.start()
