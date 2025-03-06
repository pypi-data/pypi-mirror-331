import os
from time import sleep

from polaris import CeresClient, RegisterInstance, InstanceRequest
import unittest


class TestCeresClient(unittest.TestCase):
    def setUp(self):
        self.address = os.getenv('POLARIS_ADDRESS', default='ceres-rd.weizhipin.com')
        self.namespace = os.getenv('POLARIS_NAMESPACE', default='my-namespace')
        self.service = os.getenv('POLARIS_SERVICE', default='my-service')
        self.token = os.getenv('POLARIS_TOKEN', default='******')

    def tearDown(self):
        pass

    def test_get_healthy_instance(self):
        try:
            cc = CeresClient(_host=self.address)
            instances = cc.get_healthy_instances(InstanceRequest(namespace=self.namespace, service=self.service))
            self.assertTrue(len(instances) > 0)
        except Exception as e:
            raise e

    def test_get_one_instance(self):
        try:
            cc = CeresClient(_host=self.address)
            for i in range(0, 100):
                instance = cc.get_one_instance(InstanceRequest(namespace=self.namespace, service=self.service))
                self.assertTrue(instance is not None)
        except Exception as e:
            raise e

    def test_get_one_instance_hash(self):
        try:
            cc = CeresClient(_host=self.address)
            host = ''
            for i in range(0, 100):
                instance = cc.get_one_instance(InstanceRequest(namespace=self.namespace, service=self.service, hash_key='1'))
                self.assertTrue(instance is not None)
                if host != '':
                    self.assertEqual(host, instance.host)
                host = instance.host
        except Exception as e:
            raise e

    def test_get_instance_bench(self):
        try:
            cc = CeresClient(_host=self.address)
            for i in range(0, 100000):
                instance = cc.get_one_instance(InstanceRequest(namespace=self.namespace, service=self.service))
                self.assertTrue(instance is not None)
        except Exception as e:
            raise e

    def test_get_instance_hash_bench(self):
        try:
            cc = CeresClient(_host=self.address)
            host = ''
            for i in range(0, 100000):
                instance = cc.get_one_instance(InstanceRequest(namespace=self.namespace, service=self.service, hash_key='1'))
                if host != '':
                    self.assertEqual(host, instance.host)
                host = instance.host
        except Exception as e:
            raise e

    def test_register(self):
        try:
            cc = CeresClient(_host=self.address, _token=self.token)
            instance = RegisterInstance(id='test-regi-1', namespace=self.namespace, service=self.service, host='1.1.1.1',
                                        port=1234)
            instance2 = RegisterInstance(namespace=self.namespace, service=self.service, host='1.1.1.1', port=1234)
            response = cc.register_instance(instance)
            response2 = cc.register_instance(instance2)
            response3 = cc.register_instance(instance2)
            response4 = cc.register_instance(instance2)
            self.assertTrue(response is not None)
            self.assertEqual(response2.__dict__, response3.__dict__)
            self.assertEqual(response2.__dict__, response4.__dict__)

        except Exception as e:
            print("request error:", e)
            raise e
        # ...

        # 注册id
        instance.id = response.id
        instance2.id = response2.id

        # 程序退出前反注册
        self.assertTrue(cc.deregister_instance(instance) is not None)
        self.assertTrue(cc.deregister_instance(instance2) is not None)

    def test_get_one_instance_bench(self):
        try:
            cc = CeresClient(_host=self.address)
            for i in range(0, 100000):
                instance = cc.get_one_instance(InstanceRequest(namespace=self.namespace, service=self.service))
                self.assertTrue(instance is not None)
        except Exception as e:
            raise e

    def test_register_bench(self):
        try:
            cc = CeresClient(_host=self.address, _token=self.token)
            for i in range(0, 100):
                instance = cc.register_instance(RegisterInstance(
                    namespace=self.namespace,
                    service=self.service,
                    host='1.1.1.1',
                    port=1000+i))
                self.assertTrue(instance is not None)
            sleep(30)
            for i in range(0, 100):
                instance = cc.deregister_instance(RegisterInstance(
                    namespace=self.namespace,
                    service=self.service,
                    host='1.1.1.1',
                    port=1000+i))
                self.assertTrue(instance is not None)
        except Exception as e:
            raise e


if __name__ == '__main__':
    unittest.main()
