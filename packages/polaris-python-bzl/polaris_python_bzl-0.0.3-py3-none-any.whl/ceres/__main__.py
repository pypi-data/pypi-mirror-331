#!/usr/bin/env python
import argparse
import json

from ceres.polaris import RegisterInstance, CeresClient, InstanceRequest


def register_instance(cc:CeresClient, instance:RegisterInstance):
    # 注册示例
    inst = cc.register_instance(instance)
    instance.id = inst.id
    print('register:', json.dumps(inst.__dict__ if inst is not None else {}, indent=2))


def register_instance_count(cc:CeresClient, instance_count:int, instance:RegisterInstance):
    ids = []
    for _ in range(instance_count):
        instance.port = instance.port+1
        inst = cc.register_instance(instance)
        instance.id = inst.id
        ids.append(inst.id)

    for _id in ids:
        _ = cc.deregister_instance(RegisterInstance(id=_id, namespace=instance.namespace, service=instance.service))


def deregister_instance(cc:CeresClient, instance:RegisterInstance):
    # 反注册示例
    inst = cc.deregister_instance(instance)
    instance.id = inst.id
    print('deregister:', json.dumps(inst.__dict__ if inst is not None else {}, indent=2))


def discover_instance(cc:CeresClient, count, namespace, service, hash_key=None):
    # 发现实例
    dic = dict()
    for i in range(0, count):
        inst = cc.get_one_instance(InstanceRequest(namespace, service, hash_key=hash_key))
        h = '%s:%d' % (inst.host,inst.port) if inst is not None else None
        if h is not None:
            dic[h] = dic.get(h, 0) + 1
    print(json.dumps(dic, indent=2))


if __name__ == '__main__':
    ap = argparse.ArgumentParser('ceres-tools')
    host_group = ap.add_mutually_exclusive_group(required=False)
    host_group.add_argument('--host', '-H', default='127.0.0.1', help='the host of polaris server')
    host_group.add_argument('--env', '-e', default=None, help='the environment of polaris server')
    ap.add_argument('--port', '-P', default=8090, help='the port of polaris server', type=int)
    ap.add_argument('--token', '-t', default='', help='the polaris token')
    ap.add_argument('--namespace', '-n', default='bzl-infra', help='the namespace')
    ap.add_argument('--service', '-s', default='my-service', help='the service')
    ap.add_argument('--count', '-c', default=1, type=int, help='discover count')
    ap.add_argument('--key', '-k', default=None, help='discover hash key')
    group = ap.add_mutually_exclusive_group(required=False)
    group.add_argument('--register', '-r', action='store_true', default=False, help='register instance, disable healthcheck')
    group.add_argument('--deregister', '-d', action='store_true', default=False, help='deregister instance')
    group.add_argument('--bench', '-b', action='store_true', default=False, help='benchmark register instance')
    ap.add_argument('--instance-host', '-i', default='127.0.0.1', help='register instance host')
    ap.add_argument('--instance-port', '-p', default=0, type=int, help='register instance port')
    ap.add_argument('--instance-id', '-id', default=None, help='register/deregister instance id')

    args, argv = ap.parse_known_args()
    _cc = CeresClient('ceres-%s.weizhipin.com' % args.env if args.env is not None else args.host, args.port, args.token)
    if args.register:
        register_instance(_cc, RegisterInstance(namespace=args.namespace,
                                                service=args.service,
                                                host=args.instance_host,
                                                port=args.instance_port,
                                                enable_health_check=False))
    elif args.deregister:
        deregister_instance(_cc, RegisterInstance(id=args.instance_id,
                                                  namespace=args.namespace,
                                                  service=args.service,
                                                  host=args.instance_host,
                                                  port=args.instance_port))
    elif args.bench:
        register_instance_count(_cc, args.count, RegisterInstance(
                                                  namespace=args.namespace,
                                                  service=args.service,
                                                  host=args.instance_host,
                                                  port=args.instance_port))
    else:
        discover_instance(_cc, args.count, args.namespace, args.service, hash_key=args.key)
