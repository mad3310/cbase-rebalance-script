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


MAIN_HOST = util.MAIN_HOST
PORT = util.PORT
USER = util.USER
PASSWORD = util.PASSWORD

old_container_names = util.old_container_names
new_container_names = util.new_container_names
name_ips = util.name_ips


def get_new_container_name(cluster_name):
    curs = set(get_container_names(cluster_name).keys())
    new_container_names.update(curs - old_container_names)
    assert new_container_names
    return new_container_names.pop()


def get_old_container_name():
    return old_container_names


def update_old_container_names(contaienr_name):
    old_container_names.add(contaienr_name)


def init_data(cluster_name):
    old_container_names.update(get_container_names(cluster_name).keys())
    assert old_container_names


def expand_container(cluster_name):

    def check_res(cluster_name):
        import time
        time.sleep(5)
        _, data = http_request(MAIN_HOST, PORT, user=(
            USER, PASSWORD), method='GET', path='/containerCluster/createResult/%s' % cluster_name)
        obj = json.loads(data)
        retry_count = 20
        while obj['response']['code'] != '000000' and retry_count > 0:
            time.sleep(3)
            _, data = http_request(MAIN_HOST, PORT, user=(
                USER, PASSWORD), method='GET', path='/containerCluster/createResult/%s' % cluster_name)
            obj = json.loads(data)
            retry_count -= 1

        if retry_count <= 0:
            raise Exception("expand container failed")

    data = {
        "containerClusterName": cluster_name,
        "componentType": "cbase",
        "networkMode": "ip",
        "nodeCount": "1",
        "image": "10.160.140.32:5000/lihanlin1/cbase:V4",
    }
    code, data = http_request(
        MAIN_HOST, PORT, (USER, PASSWORD), 'POST', '/containerCluster/node', data)
    assert code == 200

    check_res(cluster_name)


def config_cbase(cluster_name):

    cbase_user = "root"
    cbase_pwd = cluster_name
    cbase_port = 8091

    def add_node(cluster_name):
        new_container = get_new_container_name(cluster_name)
        new_ip = name_ips[new_container]
        old_ip = name_ips[list(get_old_container_name())[0]]

        data = {
            "hostname": new_ip,
            "user": cbase_user,
            "password": cbase_pwd
        }

        code, data = http_request(
            old_ip, cbase_port, (cbase_user, cbase_pwd), 'POST', '/controller/addNode', data)
        assert code == 200
        update_old_container_names(new_container)
        obj = json.loads(data)
        return obj["otpNode"]

    def rebalance(new_node):
        pair = new_node.split("@")
        node_flag = pair[0]
        new_ip = pair[1]

        names = get_old_container_name()
        nodes = []
        for name in names:
            nodes.append("%s@%s" % (node_flag, name_ips[name]))
        str_nodes = ','.join(nodes)
        data = {
            "knownNodes": str_nodes
        }
        code, data = http_request(
            new_ip, cbase_port, (cbase_user, cbase_pwd), 'POST', '/controller/rebalance', data)
        assert code == 200

    def check_res(new_node):
        new_ip = new_node.split("@")[1]
        code, data = http_request(
            new_ip, cbase_port, (cbase_user, cbase_pwd), 'GET', '/pools/default/rebalanceProgress', {})
        assert code == 200
        obj = json.loads(data)
        while obj["status"] == "none":
            _, data = http_request(
                new_ip, cbase_port, (cbase_user, cbase_pwd), 'GET', '/pools/default/rebalanceProgress', {})
            obj = json.loads(data)

    new_node = add_node(cluster_name)
    rebalance(new_node)
    check_res(new_node)


def parse_cmd():

    def check_input(options):
        if not (options.clustername and options.number):
            raise Exception(
                "please check input both clustername and expand number")

    parser = OptionParser()
    parser.add_option("-c", "--cluster",
                      help="expand cluster name", dest="clustername")
    parser.add_option("-n", "--number",
                      help="expand node number", dest="number")
    (options, args) = parser.parse_args()
    check_input(options)
    return options


def auto_expand(cluster_name, num):

    total = num + 1
    while num > 0:
        index = total - num
        print 'start expand cbase node:%d' % index
        init_data(cluster_name)
        print 'init data ok'
        expand_container(cluster_name)
        print 'expand container ok'
        config_cbase(cluster_name)
        print 'rebalance cbase ok'
        print 'expand cbase node %d success' % index
        print
        num -= 1


if __name__ == "__main__":
    options = parse_cmd()
    auto_expand(options.clustername, int(options.number))
    clear()
