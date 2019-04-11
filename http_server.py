#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import time
import urlparse
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler


class MyHttpHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            # send html message
            self.wfile.write('Hello World')
            return
        if self.path == '/get_current_time/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            # send html message(for iframe-streaming)
            count = 0
            while True:
                current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                html_string = """<script type="text/javascript">
                parent.document.getElementById('current-time').innerHTML = '{current_time}';
                </script>
                """.format(current_time=current_time)
                self.wfile.write(html_string)
                count += 1
                print('iframe-streaming response count: {count}'.format(count=count))
                time.sleep(1)
        elif self.path.startswith('/get_current_time/'):
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            # self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            # send json message
            parsed_path = urlparse.urlparse(self.path)
            params = urlparse.parse_qs(parsed_path.query)
            callback = params.get('callback')[0]
            result = {
                'code': 200,
                'data': dict(
                    current_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                )
            }
            jsonp_result = callback + "(" + json.dumps(result) + ")"
            self.wfile.write(jsonp_result)
            return
        else:
            self.send_error(404, 'Page not found.')
            return


if __name__ == '__main__':
    server = HTTPServer(('localhost', 9000), MyHttpHandler)
    print('http server is running at http://localhost:9000. Press Ctrl+C to stop.')
    server.serve_forever()
