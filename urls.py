from handlers.statusimages import StatusImagesHandler
from handlers.api import ApiHandler
from tornado import web

multicast_ip = "2[0-9]{1,2}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}:[0-9]{1,5}"

url_patterns = [
    (r"/status/images", StatusImagesHandler),
    (r"/channels?", ApiHandler),
    (r"/channels/%s" % multicast_ip, ApiHandler),
    (r"/channels/new", ApiHandler),
    (r"/channels/images/(.*)", web.StaticFileHandler, {"path": "/tmp/wambo/1/channels/images/"}),
    (r"/.*", ApiHandler),
]
