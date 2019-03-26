#!/usr/bin/env python
# -*- coding: utf-8 -*-

from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
import cgi
import time


class MyHttpHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path != '/':
            self.send_error(404, 'File not found.')
            return

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        # send html message,
        self.wfile.write('Hello World')
        return

    def do_POST(self):
        ctype, pdict = cgi.parse_header(self.headers['content-type'])
        if ctype == 'application/json':
            post_data = dict(
                current_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            )
        else:
            self.send_error(415, "Only json data is supported.")
            return

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        self.wfile.write(post_data)


if __name__ == '__main__':
    server = HTTPServer(('127.0.0.1', 9000), MyHttpHandler)
    print("Starting server, use <Ctrl-C> to stop")
    server.serve_forever()
