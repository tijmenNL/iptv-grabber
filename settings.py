import logging
import tornado
import tornado.template
import os
from tornado.options import define, options
from application.process import process, ProcessError
from application.configuration import ConfigSection, ConfigSetting

import environment
import logconfig

# Make filepaths relative to settings.
path = lambda root,*a: os.path.join(root, *a)
ROOT = os.path.dirname(os.path.abspath(__file__))
cfg_filename = 'config.ini'

system_config_directory = '/etc/vice'
runtime_directory = '/var/run/vice-iptv-grabber'
default_pid = os.path.join(runtime_directory, 'server.pid')
default_config = os.path.join(system_config_directory, cfg_filename)
fullname = 'VICE IPTV Grabber'
version = '0.1.0'

define("port", default=8668, help="run on the given port", type=int)
define("config", default=None, help="tornado config file")
define("debug", default=False, help="debug mode")
define('config_file', default=default_config, help='configuration file', metavar='FILE')
tornado.options.parse_command_line()

MEDIA_ROOT = path(ROOT, 'media')
TEMPLATE_ROOT = path(ROOT, 'templates')

# Deployment Configuration

class DeploymentType:
    PRODUCTION = "PRODUCTION"
    DEV = "DEV"
    SOLO = "SOLO"
    STAGING = "STAGING"
    dict = {
        SOLO: 1,
        PRODUCTION: 2,
        DEV: 3,
        STAGING: 4
    }

if 'DEPLOYMENT_TYPE' in os.environ:
    DEPLOYMENT = os.environ['DEPLOYMENT_TYPE'].upper()
else:
    DEPLOYMENT = DeploymentType.SOLO

settings = {}
#settings['debug'] = DEPLOYMENT != DeploymentType.PRODUCTION or options.debug
settings['debug'] = True
settings['static_path'] = MEDIA_ROOT
settings['cookie_secret'] = "your-cookie-secret"
settings['xsrf_cookies'] = False
settings['template_loader'] = tornado.template.Loader(TEMPLATE_ROOT)

SYSLOG_TAG = "boilerplate"
SYSLOG_FACILITY = logging.handlers.SysLogHandler.LOG_LOCAL2

# See PEP 391 and logconfig for formatting help.  Each section of LOGGERS
# will get merged into the corresponding section of log_settings.py.
# Handlers and log levels are set up automatically based on LOG_LEVEL and DEBUG
# unless you set them here.  Messages will not propagate through a logger
# unless propagate: True is set.
LOGGERS = {
    'loggers': {
        'boilerplate': {},
    },
}

if settings['debug']:
    LOG_LEVEL = logging.DEBUG
else:
    LOG_LEVEL = logging.INFO
USE_SYSLOG = DEPLOYMENT != DeploymentType.SOLO

logconfig.initialize_logging(SYSLOG_TAG, SYSLOG_FACILITY, LOGGERS,
        LOG_LEVEL, USE_SYSLOG)

if options.config:
    tornado.options.parse_config_file(options.config)

cpath, cfg_file = os.path.split(options.config_file)
if path:
    system_config_directory = cpath

process.system_config_directory = system_config_directory
cfg_filename = process.config_file(cfg_file)

class Port(int):

    def __new__(cls, value):
        value = int(value)
        if not (0 <= value <= 65535):
            raise ValueError("illegal port value: %s" % value)
        return value


class GeneralConfiguration(ConfigSection):
    __cfgfile__ = cfg_filename
    __section__ = 'settings'

    server = ConfigSetting(type=str, value=None)
    port = ConfigSetting(type=Port, value=80)
    path = ConfigSetting(type=str, value='api')

logger = logging.getLogger('boilerplate.' + __name__)

if cfg_filename:
    logger.info("Starting %s %s, config=%s" %
            (fullname, version, cfg_filename))
    settings['server'] = GeneralConfiguration.server
    settings['port'] = GeneralConfiguration.port
    settings['path'] = GeneralConfiguration.path
    settings['version'] = version
else:
    logger.fatal("Starting %s %s, with no configuration file" %
              (fullname, version))
    sys.exit(1)
