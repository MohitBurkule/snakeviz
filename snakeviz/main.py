#!/usr/bin/env python

import os
import os.path
from pstats import Stats
import json
import urllib.parse
import http.server
import socketserver

from .stats import table_rows, json_stats

STATIC_DIR = os.path.join(os.path.dirname(__file__), 'static')
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')


class VizHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        profile_name = parsed_url.path.split('/')[-1]

        abspath = os.path.abspath(profile_name)
        if os.path.isdir(abspath):
            self.list_dir(abspath)
        else:
            try:
                s = Stats(profile_name)
            except Exception as e:
                raise RuntimeError('Could not read %s.' % profile_name) from e
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(self.render_template('viz.html', profile_name=profile_name, table_rows=table_rows(s), callees=json_stats(s)))

    def list_dir(self, path):
        entries = os.listdir(path)
        dir_entries = [[['..', urllib.parse.quote(os.path.normpath(os.path.join(path, '..')), safe='')]]]
        for name in entries:
            if name.startswith('.'):
                # skip invisible files/directories
                continue
            fullname = os.path.join(path, name)
            displayname = linkname = name
            # Append / for directories or @ for symbolic links
            if os.path.isdir(fullname):
                displayname += '/'
            if os.path.islink(fullname):
                displayname += '@'
            dir_entries.append([[displayname, urllib.parse.quote(os.path.join(path, linkname), safe='')]])

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(self.render_template('dir.html', dir_name=path, dir_entries=json.dumps(dir_entries)))

    def render_template(self, template_name, **kwargs):
        with open(os.path.join(TEMPLATE_DIR, template_name), 'rb') as f:
            template_content = f.read()
        return template_content


class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    pass


if __name__ == '__main__':
    server_address = ('', 8080)
    httpd = ThreadedHTTPServer(server_address, VizHandler)
    print("Server running at http://127.0.0.1:8080/")
    httpd.serve_forever()
