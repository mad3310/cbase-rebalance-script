__author__ = 'xsank'

import sys
import json
import time
import urllib
import httplib
import base64
from optparse import OptionParser

import util
from util import clear
from util import http_request


MAIN_HOST = util.MAIN_HOST
PORT = util.PORT
USER = util.USER
PASSWORD = util.PASSWORD


def recover(cluster_name,node_ip):
    pass


def parse_cmd():

    def check_input(options):
        if not (options.clustername and options.nodeip):
            raise Exception(
                "please check input both clustername and nodeip")

    parser = OptionParser()
    parser.add_option("-c", "--cluster",
                      help="expand cluster name", dest="clustername")
    parser.add_option("-n", "--nodeip",
                      help="recover node ip", dest="nodeip")
    (options, args) = parser.parse_args()
    check_input(options)
    return options


if __name__=="__main__":
    options=parse_cmd()
    recover(options.clustername,options.nodeip)
    clear()