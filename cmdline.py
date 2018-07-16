# -*- coding: utf-8 -*-
import os
import sys
import argparse
from tornado import web
from tornado import httpserver
from tornado import ioloop
import tornado.platform.twisted
tornado.platform.twisted.install()


arguments = None
project_settings = None


def parse_arguments():

    def valid_setting(string):
        key, sep, value = string.partition('=')
        if not key or not sep:
            raise argparse.ArgumentTypeError(
                u'expected name=value: {}'.format(repr(string)))
        return key, value

    parser = argparse.ArgumentParser(
        description='HTTP API server for scrapytornado project.')
    parser.add_argument('-p', '--port', dest='port',
                        type=int,
                        default=9080,
                        help='port number to listen on')
    parser.add_argument('-i', '--ip', dest='ip',
                        default='localhost',
                        help='IP address the server will listen on')
    parser.add_argument('--project', dest='project',
                        default='default',
                        help='project name from scrapy.cfg')
    parser.add_argument('-s', '--set', dest='set',
                        type=valid_setting,
                        action='append',
                        default=[],
                        metavar='name=value',
                        help='set/override setting (may be repeated)')
    parser.add_argument('-S', '--settings', dest='settings',
                        metavar='project.settings',
                        help='custom project settings module path')
    return parser.parse_args()


def get_application():
    from app import TrackingsHandler
    from app import AfterShip404Handler
    return web.Application([
        (r"/trackings", TrackingsHandler),
        (r"(.*)", AfterShip404Handler)
    ])


def execute():
    global arguments
    global project_settings
    sys.path.insert(0, os.getcwd())
    arguments = parse_arguments()
    application = get_application()
    server = httpserver.HTTPServer(application)
    server.listen(arguments.port)
    ioloop.IOLoop.current().start()


if __name__ == '__main__':
    execute()
