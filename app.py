#!/usr/bin/env python

import tornado.httpserver

from tornado.httpclient import AsyncHTTPClient

from tornado.ioloop import IOLoop
from tornado_pyuv import UVLoop
IOLoop.configure(UVLoop)

from tornado.escape import json_encode
import cjson
import tornado.web
import socket
from tornado.options import options

from settings import settings
from urls import url_patterns
import urllib


class TornadoBoilerplate(tornado.web.Application):
    def __init__(self):
        tornado.web.Application.__init__(self, url_patterns, **settings)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((viceIp, vicePort))
        address = s.getsockname()[0]
        body = cjson.encode(Status(address))
        headers = {"Content-Type": "application/json"}
        print body
        request = tornado.httpclient.HTTPRequest(url='%s/frontend_test.php/role_status' % viceServer, method='POST', body=body, headers=headers)
        client = tornado.httpclient.AsyncHTTPClient()
        client.fetch(request, callback=self.web_handle_request)

    def web_handle_request(self, response):
        if response.error:
            print "Error:", response.error
        else:
            print response.body

viceIp = settings['server']
vicePort = settings['port']
vicePath = settings['path']
viceServer = 'http://' + viceIp + ':' + str(vicePort) + '/' + vicePath


def Status(ip):
    grabberstatus = {}
    grabberstatus['uptime'] = 1
    grabberstatus['role_type'] = "grab_digital"
    grabberstatus['port'] = "8668"
    grabberstatus['ip'] = ip
    grabberstatus['version'] = settings['version']
    return grabberstatus


def main():
    app = TornadoBoilerplate()
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)

    loop = tornado.ioloop.IOLoop.instance()
    loop.start()


if __name__ == "__main__":
    main()
