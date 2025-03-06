#!/usr/bin/env python

"""
RocketMQ python 客户端， 使用http协议与polaris服务端通信
"""
import sys

if sys.version_info < (3, 0):
    raise Exception("Python 3 or a more recent version is required.")

import os
import json
import time
import logging
from logging.handlers import RotatingFileHandler
from random import random
from time import sleep
from http import client
import _thread as thread


POLARIS_BASE_PATH = os.getenv("POLARIS_BASE_PATH", "./polaris")


def _init_logger(name='polaris', filename='polaris.log', level=logging.INFO):
    # init log
    os.makedirs(POLARIS_BASE_PATH + "/log/", exist_ok=True)
    _log = logging.getLogger(name)

    handler = RotatingFileHandler(POLARIS_BASE_PATH + "/log/" + filename, maxBytes=10*1024*1024, backupCount=10)
    logging.StreamHandler()
    handler.setLevel(level)
    fmt = '%(asctime)s %(levelname)s %(filename)s %(lineno)d %(process)d %(message)s'
    date_fmt = '%Y-%m-%d %H:%M:%S'
    handler.setFormatter(logging.Formatter(fmt, datefmt=date_fmt))
    _log.addHandler(handler)
    _log.setLevel(logging.INFO)
    return _log


log = _init_logger()


class HttpClient:
    def __init__(self, host, port, max_alive = 120):
        self._connection = client.HTTPConnection(host, port, timeout=5)
        self._last_access = time.time()
        self._max_alive = max_alive
        self._lock = thread.allocate_lock()

    def get(self):
        return self._connection

    def request(self, method:str, url:str, body, headers, resp_func=None):
        self.refresh()
        with self._lock:
            response = None
            try:
                self._connection.request(method=method, url=url, body=body, headers=headers)
                response = self._connection.getresponse()
                if response.status != 200:
                    code = response.getheader('X-Polaris-Code', None)
                    msg = response.getheader('X-Polaris-Message', None)
                    raise Exception('status error: %d, response code: %s, response msg: %s' % (response.status, code, msg))
                return resp_func(response) if resp_func is not None else response.read()
            except Exception as e:
                log.error("http error: %s", e.__str__(), exc_info=True)
                raise e
            finally:
                if response is not None:
                    response.close()

    def outdated(self):
        return 0 < self._max_alive < time.time() - self._last_access

    def refresh(self):
        self._last_access = time.time()

    def close(self):
        self._connection.close()


class ClientManager:
    def __init__(self, host, port):
        self._host = host
        self._port = port
        self._default_client = HttpClient(host, port, -1)
        self._clients = {}
        self._clients_lock = thread.allocate_lock()
        self._running = True
        self._start()

    def stop(self):
        self._running = False

    def get(self, host:str):
        if host is None:
            return self._default_client
        with self._clients_lock:
            if self._clients.get(host, None) is not None:
                self._clients[host].refresh()
                return self._clients[host]
            else:
                self._clients[host] = HttpClient(host, self._port)
                return self._clients[host]

    def request(self, host:str, method:str, url:str, data, headers, resp_func=None):
        return self.get(host).request(method=method, url=url, body=data, headers=headers, resp_func=resp_func)

    def _start(self):
        def _auto_clean():
            while self._running:
                deleting = []
                with self._clients_lock:
                    for k, v in self._clients.items():
                        if v.outdated():
                            log.info("closing client: %s", k)
                            deleting.append(self._clients.pop(k))
                for c in deleting:
                    c.close()
                sleep(10)
                log.info('clear [%s]', ','.join(deleting))

        log.info("start auto clean thread")
        thread.start_new_thread(_auto_clean, ())


class CacheManager:
    _CACHE_DEFAULT_PATH = POLARIS_BASE_PATH + "/backup/"
    _CACHE_DEFAULT_SUFFIX = ".json"
    def __init__(self, path=None):
        self._path = path if path is not None and path != '' else self._CACHE_DEFAULT_PATH
        self._data_lock = thread.allocate_lock()
        self._data_set = {}
        self._running = True
        self._start()

    def put(self, key, data):
        with self._data_lock:
            self._data_set[key] = data

    def get(self, key):
        with self._data_lock:
            return self._data_set.get(key)

    def _start(self):
        log.info("start auto save thread")
        thread.start_new_thread(self._save, ())

    def _save(self):
        while self._running:
            data_copy = {}
            with self._data_lock:
                for k, v in self._data_set.items():
                    data_copy[k] = v
            os.makedirs(self._path, exist_ok=True)
            for k, v in data_copy.items():
                with open(self._path + k + self._CACHE_DEFAULT_SUFFIX, 'w') as f:
                    f.write(json.dumps(v.origin(), indent=2))
            sleep(3)


class RegisterInstance:
    def __init__(self, **kwargs):
        # id 选填， 若注册时使用id需保证id的唯一性, 并且反注册必须携带该id
        self.id = kwargs.get('id')
        # namespace, 注册必填， 命名空间， 若反注册使用id， 可不填
        self.namespace = kwargs.get('namespace')
        # service, 注册必填， 服务名称， 若反注册使用id， 可不填
        self.service = kwargs.get('service')
        # host, 注册必填， 服务地址， 若反注册使用id， 可不填
        self.host = kwargs.get('host')
        # port, 注册必填， 服务端口， 若反注册使用id， 可不填
        self.port = kwargs.get('port')
        # protocol 选填， 协议
        self.protocol = kwargs.get('protocol')
        # protocol 选填， 版本
        self.version = kwargs.get('version')
        # protocol 选填， 优先级
        self.priority = kwargs.get('priority')
        # protocol 选填， 权重
        self.weight = kwargs.get('weight')
        # enable_health_check 选填， 启用健康检查
        self.enable_health_check = kwargs.get('enable_health_check', True)
        # health_check, 选填， 健康检查参数
        self.health_check = {
            "type": 1,
            "heartbeat": {
                "ttl": kwargs.get('ttl'),
            },
        }
        # healthy 选填，默认的健康状态
        self.healthy = True
        # isolate 选填，默认的隔离状态
        self.isolate = False
        # location 选填，位置信息
        self.location = {
            "region": kwargs.get('region',),
            "zone": kwargs.get('zone'),
            "campus": kwargs.get('campus'),
        }
        # metadata 选填，其他信息
        self.metadata = {
            "region": kwargs.get('region'),
            "zone": kwargs.get('zone'),
            "campus": kwargs.get('campus'),
        }
        if type(kwargs.get('metadata')) is dict:
            for k, v in kwargs.get('metadata').items():
                self.metadata[k] = v
        # logic_set 选填
        self.logic_set = kwargs.get('logic_set')
        # service_token 选填， HTTP 接口使用 header 进行认证， 这里的token无作用
        self.service_token = kwargs.get('service_token')


class Service:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.name = kwargs.get('name')
        self.namespace = kwargs.get('namespace')
        self.metadata = kwargs.get('metadata')
        self.revision = kwargs.get('revision')


class Instance:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.service = kwargs.get('service')
        self.namespace = kwargs.get('namespace')
        self.host = kwargs.get('host')
        self.port = kwargs.get('port')
        self.protocol = kwargs.get('protocol')
        self.version = kwargs.get('version')
        self.priority = kwargs.get('priority')
        self.weight = kwargs.get('weight')
        self.enableHealthCheck = kwargs.get('enableHealthCheck')
        self.healthCheck = kwargs.get('healthCheck')
        self.healthy = kwargs.get('healthy')
        self.isolate = kwargs.get('isolate')
        self.location = kwargs.get('location')
        self.metadata = kwargs.get('metadata')
        self.logic_set = kwargs.get('logic_set')
        self.ctime = kwargs.get('ctime')
        self.mtime = kwargs.get('mtime')
        self.revision = kwargs.get('revision')

    def is_healthy(self):
        # None => healthy
        return self.healthy is None or self.healthy

    def is_isolate(self):
        # None => not isolate
        return self.isolate is not None and self.isolate

    def is_zero_weight(self):
        # None => weight != 0
        return self.weight is not None and self.weight == 0

    def is_valid(self, filter_func = None):
        # valid instance: healthy && not isolate && weight != 0
        return self.is_healthy() and not self.is_isolate() and not self.is_zero_weight() \
            and (filter_func is None or filter_func(self))


class InstanceRequest:
    def __init__(self, namespace:str, service:str, hash_key:str = None, filter_func = None):
        self.namespace = namespace
        self.service = service
        self.hash_key = hash_key
        self.filter_func = filter_func


class PolarisResponse(json.JSONDecoder):
    _RESPONSE_OK = 200000
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.code = 0
        self.info = ''
        self.type = None
        self.service = None
        self.instance = None
        self.instances = None
        self.routing = None
        self.rateLimit = None
        self.circuitBreaker = None
        self.services = None
        self.namespaces = None
        self.faultDetector = None
        self.aliasFor = None
        self.serviceContract = None
        self._origin = None

    def ok(self):
        return self.code == self._RESPONSE_OK

    def decode(self, s: str, **kwargs):
        decoded = super().decode(s, **kwargs)
        self._origin = decoded
        if type(decoded) is dict:
            return self.parse_to_self(**decoded)
        else:
            raise Exception('decode error')

    # origin dict
    def origin(self):
        return self._origin

    def parse_to_self(self, **kwargs):
        self.code = kwargs.get('code')
        self.info = kwargs.get('info')
        self.type = kwargs.get('type')
        self.routing = kwargs.get('routing')
        self.rateLimit = kwargs.get('rateLimit')
        self.circuitBreaker = kwargs.get('circuitBreaker')
        self.services = kwargs.get('services')
        self.namespaces = kwargs.get('namespaces')
        self.faultDetector = kwargs.get('faultDetector')
        self.serviceContract = kwargs.get('serviceContract')

        ##
        self.instance = self._instance(kwargs.get('instance'))
        self.instances = self._instances(kwargs.get('instances'))
        self.service = self._service(kwargs.get('service'))
        self.aliasFor = self._service(kwargs.get('aliasFor'))

        return self

    @staticmethod
    def _valid_list(_lst):
        return _lst is not None and type(_lst) is list

    @staticmethod
    def _valid_dict(_dct):
        return _dct is not None and type(_dct) is dict

    def _service(self, _data:dict) -> Service:
        return Service(**_data) if self._valid_dict(_data) else None

    def _instance(self, _data:dict) -> Instance:
        return Instance(**_data) if self._valid_dict(_data) else None

    def _instances(self, _data:list):
        instances = [Instance(**_i) for _i in _data if self._valid_dict(_i)] if self._valid_list(_data) else None
        if instances is not None:
            instances.sort(key=lambda k: (k.priority, k.id), reverse=True)
        return instances


class CeresClient:
    """ Polaris python客户端 (使用http协议通信)
    """
    _DISCOVER_URL = "/v1/Discover"
    _REGISTER_URL = "/v1/RegisterInstance"
    _DEREGISTER_URL = "/v1/DeregisterInstance"
    _HEARTBEAT_URL = "/v1/Heartbeat"
    _POLARIS_SEP = "#"

    _POLARIS_NAMESPACE = "Polaris"
    _POLARIS_DISCOVER_SERVICE = "polaris.discover"
    _POLARIS_HEALTHCHECK_SERVICE = "polaris.healthcheck"

    def __init__(self, _host='127.0.0.1', _port=8090, _token=''):
        self._host = _host
        self._port = _port
        self._token = _token if _token is not None else ''
        self._header = {
            "Content-Type": "application/json",
            "X-Polaris-Token": self._token
        }
        self._client_manager = ClientManager(self._host, self._port)
        self._cache_manager = CacheManager()

        self._keys_lock = thread.allocate_lock()
        self._keys = {}

        self._heartbeat_thread_id = {}
        self._heartbeat_thread_id_lock = thread.allocate_lock()

        self.initialized = False
        self._start()

    def get_all_instances(self, req:InstanceRequest, force_update=False):
        _key = self._build_key(req.namespace, req.service)
        with self._keys_lock:
            self._keys[_key] = True
        response = self._cache_manager.get(_key)
        if response is None or force_update:
            try :
                log.debug('get instances: namespace=%s, service=%s', req.namespace, req.service)
                if req.namespace == self._POLARIS_NAMESPACE and req.service == self._POLARIS_DISCOVER_SERVICE:
                    # discover 首次寻址
                    host = None
                else:
                    host = self._select_discover_instance()
                response = self._discover(1, namespace=req.namespace, service=req.service, host=host)
                self._cache_manager.put(_key, response)
            except Exception as e:
                log.error('get instances error: %s', e.__str__(), exc_info=True)
                raise e
        return self._fetch_instances(response, req.filter_func)

    def get_healthy_instances(self, req:InstanceRequest):
        origin = req.filter_func
        req.filter_func = lambda _i: _i is not None and _i.is_valid(origin)
        return self.get_all_instances(req)

    def get_one_instance(self, req:InstanceRequest):
        instances = self.get_healthy_instances(req)
        if req.hash_key is None:
            return self._select_instance_weight(instances)
        else:
            return self._select_instance_hash(instances, req.hash_key)

    def register(self, instance:RegisterInstance) -> Instance:
        response = self._register(instance=instance, host=self._select_discover_instance())
        if response is None :
            raise Exception('register fail: response not found')
        elif not response.ok():
            log.error('register fail: %s', response.info)
            raise Exception('register fail: %s' % response.info)
        else:
            return response.instance

    def register_instance(self, instance:RegisterInstance) -> Instance:
        _instance = self.register(instance)
        if _instance is None:
            raise Exception('register failed, instance not found')
        self._start_heartbeat(_instance)
        return _instance

    def deregister_instance(self, instance:RegisterInstance) -> Instance:
        response = self._deregister(host=self._select_discover_instance(), instance=instance)
        if response is None :
            raise Exception('deregister fail, response not found')
        elif not response.ok():
            log.error('deregister fail: %s', response.info)
            raise Exception('deregister fail: %s' % response.info)
        else:
            return response.instance

    def heartbeat_instance(self, instance:RegisterInstance) -> Instance:
        log.info('heartbeat(%s) [%s:%s]:[%s:%d]', instance.id, instance.namespace, instance.service, instance.host, instance.port)
        response = self._heartbeat(host=self._select_healthcheck_instance(instance.host), instance=instance)
        if response is None :
            raise Exception('heartbeat fail, response not found')
        elif not response.ok():
            log.error('heartbeat fail: %s', response.info)
            raise Exception('heartbeat fail: %s' % response.info)
        else:
            return response.instance

    def _start(self):
        instances = self.get_healthy_instances(InstanceRequest(self._POLARIS_NAMESPACE, self._POLARIS_DISCOVER_SERVICE))
        if instances is None:
            raise Exception('no discover instances found')

        self._start_get_instances()
        self.initialized = True

    def _build_key(self, namespace, service):
        return '%s%s%s' % (namespace, self._POLARIS_SEP, service)

    # 根据hash-key 获取实例
    def _select_instance_hash(self, instances, key) -> Instance:
        return instances[self._hash(key) % len(instances)] if instances is not None and len(instances) > 0 else None

    # 根据权重获取实例
    @staticmethod
    def _select_instance_weight(instances) -> Instance or None:
        l = len(instances) if instances is not None else 0
        if l == 0:
            return None

        total = 0
        index = 0
        indexes = []
        for instance in instances:
            if instance.weight > 0:
                indexes.append((total, index))
                total += instance.weight
            index = index + 1

        r = random() * total
        index = 0

        for idx in indexes:
            if idx[0] >= r:
                break
            index = idx[1]
        return instances[index % l]

    def _start_get_instances(self):
        if self.initialized:
            return
        def update_instances():
            while True:
                try:
                    local_keys = {}
                    with self._keys_lock:
                        for k, v in self._keys.items():
                            local_keys[k] = v
                    for k in local_keys.keys():
                        ns = k.split(self._POLARIS_SEP)
                        if len(ns) >= 2:
                            try:
                                self.get_all_instances(InstanceRequest(namespace=ns[0], service=ns[1]), force_update=True)
                            except Exception as e:
                                log.error('get instances fail, namespace=%s, service=%s,err=%s',
                                          ns[0], ns[1], e.__str__(), exc_info=True)
                    sleep(1)
                except Exception as e:
                    log.error('get instances fail error:%s',  e.__str__(), exc_info=True)

        # start get instances thread
        log.info('start get instances thread')
        thread.start_new_thread(update_instances, ())

    def _select_discover_instance(self):
        instances = self.get_healthy_instances(InstanceRequest(self._POLARIS_NAMESPACE, self._POLARIS_DISCOVER_SERVICE))
        if instances is None:
            return None
        one_instance = self._select_instance_weight(instances)
        return one_instance.host if one_instance is not None else None

    def _select_healthcheck_instance(self, key):
        instances = self.get_healthy_instances(InstanceRequest(self._POLARIS_NAMESPACE, self._POLARIS_HEALTHCHECK_SERVICE))
        if instances is None:
            return None
        one_instance = self._select_instance_hash(instances, key)
        return one_instance.host if one_instance is not None else None

    def _start_heartbeat(self, instance):
        _instance_id = instance.id
        _instance_name = '%s#%s#%s#%d' % (instance.namespace, instance.service,instance.host, instance.port)
        if _instance_id is None or _instance_id == '':
            _instance_id = _instance_name
        def _heartbeat_thread():
            with self._heartbeat_thread_id_lock:
                if self._heartbeat_thread_id.get(_instance_id, None) is not None:
                    log.warning('heartbeat thread %s is already running', _instance_id)
                    return
                else:
                    log.info('start heartbeat thread %s, name: %s', _instance_id, _instance_name)
                    self._heartbeat_thread_id[_instance_id] = True
            while True:
                sleep(5)
                try:
                    self.heartbeat_instance(instance)
                except Exception as e:
                    log.error('heartbeat thread fail, error: %s', e.__str__(), exc_info=True)
        thread.start_new_thread(_heartbeat_thread, ())

    @staticmethod
    def _fetch_instances(data: PolarisResponse, filter_func):
        return [instance for instance in data.instances if filter_func is None or filter_func(instance)] \
            if data is not None and data.ok() and data.instances is not None else None

    def _register(self, instance: RegisterInstance, host=None):
        return self._post(self._REGISTER_URL, headers=self._header, data=json.dumps(instance.__dict__), host=host)

    def _deregister(self, instance: RegisterInstance, host=None):
        data = {
            "id": instance.id,
            "service": instance.service,
            "namespace": instance.namespace,
            "host": instance.host,
            "port": instance.port,
        }
        return self._post(self._DEREGISTER_URL, headers=self._header, data=json.dumps(data), host=host)

    def _heartbeat(self, instance: RegisterInstance, host=None):
        return self._post(self._HEARTBEAT_URL, headers=self._header, data=json.dumps(instance.__dict__), host=host)

    def _discover(self, t, namespace:str, service:str, metadata = None, host = None):
        data = {
            "type": t,
            "service": {
                "namespace": namespace,
                "name": service,
                "metadata": metadata,
            }
        }
        return self._post(self._DISCOVER_URL, headers=self._header, data=json.dumps(data), host=host)

    def _post(self, url, headers, data, host=None) -> PolarisResponse or None:
        def _resp_func(response):
            return json.load(response, cls=PolarisResponse)
        return self._client_manager.request(host=host, method="POST", url=url, data=data, headers=headers, resp_func=_resp_func)

    @staticmethod
    def _hash(key:str):
        """稳定的str hash方法，避免每次重启hash值不一致（默认python3每次重启会有不同的seed)"""
        if type(key) == str:
            seed:int = 0
            for c in key.encode():
                seed = (31 * seed + c) % (2 ** 32)
            return seed
        else:
            return hash(key)
