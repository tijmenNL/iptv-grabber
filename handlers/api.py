from handlers.base import BaseHandler

import logging
import pyuv

import os, re

from tornado_pyuv import IOLoop

from tornado import web

logger = logging.getLogger('boilerplate.' + __name__)


class ApiHandler(BaseHandler):

    @web.asynchronous
    def get(self):
        logger.info("Got a API GET on %s " % self.request.uri)
        self.errorno = None
        self.files = None
        template_path = os.path.join(os.path.dirname(__file__), "templates")
        pyuv.fs.readdir(IOLoop.current()._loop, '/tmp/wambo/1/channels/images', 0, self.readdir_cb)

    def readdir_cb(self, loop, path, files, errorno):
        self.errorno = errorno
        not_status = re.compile('(status.*)|(thumb.*)')
        self.files = [os.path.splitext(file)[0] for file in files if not not_status.match(file)]

        self.render("base.html", files=self.files)

    def post(self):
        logger.info("Got a API POST on %s " % self.request.uri)
        self.load_json()
        print self.request.arguments
