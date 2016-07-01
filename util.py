__author__ = 'xsank'


import sys
import json
import time
import urllib
import httplib
import base64
from optparse import OptionParser


MAIN_HOST = "10.154.156.150"
PORT = 8888
USER = "root"
PASSWORD = "root"

old_container_names = set()
new_container_names = set()
name_ips = {}
name_hosts={}


def get_container_names(cluster_name):
    _, data = http_request(
        MAIN_HOST, PORT, user=(
            USER, PASSWORD), method='GET', path='/containerCluster/createResult/%s' % cluster_name)
    obj = json.loads(data)
    if obj['response']['code'] == '000000':
        for container in obj["response"]["containers"]:
            name_ips[container["containerName"]] = container["ipAddr"]
            name_hosts[container["containerName"]] = container["hostIp"]
    assert name_ips and name_hosts
    return name_ips


def get_container_host(container_name):
    return name_hosts.get(container_name,'')


def http_request(host='127.0.0.1', port=80, user=(),
                 method='GET', path='/', data={}):
    params = urllib.urlencode(data)

    headers = {
        "Content-type": "application/x-www-form-urlencoded",
        "Accept": "text/plain",
    }
    if user:
        encode_user = base64.encodestring("%s:%s" % (user[0], user[1]))[:-1]
        auth = "Basic %s" % encode_user
        headers.update({"Authorization": auth})

    con = httplib.HTTPConnection(host, port)
    con.request(method, path, params, headers)
    response = con.getresponse()
    data = response.read()
    con.close()

    return response.status, data


def clear():
    old_container_names.clear()
    new_container_names.clear()
    name_ips.clear()
    name_hosts.clear()
