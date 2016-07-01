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
from util import get_container_names
from util import get_container_host


MAIN_HOST = util.MAIN_HOST
PORT = util.PORT
USER = util.USER
PASSWORD = util.PASSWORD


def check_cluster(cluster_name):

    name_ips=get_container_names(cluster_name)

    def check_container():
        for name in name_ips:
            ip=get_container_host(name)
            _, data = http_request(
            ip, PORT, user=(
                USER, PASSWORD), method='GET', path='/container/status/%s' % name)
            res=eval(data)
            if res["response"]["status"]=="stopped":
                _,data=http_request(
                ip, PORT, user=(
                    USER, PASSWORD), method='POST', path='/container/start',data={"containerName":name})
                res=eval(data)
                if res["status"]!="started":
                    raise Exception("%s contaienr can not start" % name)

    def check_cbase():
        port=8091
        user='root'
        password=cluster_name

        bad_nodes=[]
        for ip in name_ips.values():
            code, data = http_request(
                ip, port, user=(
                    user, password), method='GET', path='/nodeStatuses')
            if code==200:
                res=eval(data)
                for k,v in res.items():
                    if v['status']!='healthy':
                        bad_nodes.append(k)
                break
        print 'bad nodes:'
        print bad_nodes

    check_container()
    check_cbase()


def parse_cmd():

    def check_input(options):
        if not options.clustername:
            raise Exception(
                "please check input clustername")

    parser = OptionParser()
    parser.add_option("-c", "--cluster",
                      help="expand cluster name", dest="clustername")
    (options, args) = parser.parse_args()
    check_input(options)
    return options


if __name__=="__main__":
    options=parse_cmd()
    check_cluster(options.clustername)
    clear()