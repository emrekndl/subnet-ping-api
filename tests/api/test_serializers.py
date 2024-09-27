import unittest
from django.test import TestCase
from rest_framework.test import APITestCase
from subnet_ip.models import IPPrefix, IPSubnets
from subnet_ip.api.serializers import IPSubnetsSerializer, IPPrefixSerializer

class TestIPSubnetsSerializer(APITestCase):
    def setUp(self):
        self.ip_prefix = IPPrefix.objects.create(ip='192.168.1.0/24', ping_task_state='SUCCESS')
        self.ip_subnet = IPSubnets.objects.create(parent_ip=self.ip_prefix, subnet='192.168.1.1', status=1)
        self.serializer = IPSubnetsSerializer(instance=self.ip_subnet)

    def test_contains_expected_fields(self):
        data = self.serializer.data
        self.assertCountEqual(data.keys(), ['id', 'parent_ip', 'subnet', 'status', 'create_date', 'update_date'])

    def test_read_only_fields(self):
        data = {'id': 999, 'create_date': '2023-01-01T00:00:00Z', 'update_date': '2023-01-01T00:00:00Z'}
        serializer = IPSubnetsSerializer(instance=self.ip_subnet, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        serializer.save()
        self.ip_subnet.refresh_from_db()
        self.assertNotEqual(self.ip_subnet.id, 999)
        self.assertNotEqual(str(self.ip_subnet.create_date), '2023-01-01 00:00:00+00:00')
        self.assertNotEqual(str(self.ip_subnet.update_date), '2023-01-01 00:00:00+00:00')

class TestIPPrefixSerializer(APITestCase):
    def setUp(self):
        self.ip_prefix = IPPrefix.objects.create(ip='192.168.1.0/24', ping_task_state='SUCCESS')
        self.ip_subnet = IPSubnets.objects.create(parent_ip=self.ip_prefix, subnet='192.168.1.1', status=1)
        self.serializer = IPPrefixSerializer(instance=self.ip_prefix)

    def test_contains_expected_fields(self):
        data = self.serializer.data
        self.assertCountEqual(data.keys(), ['id', 'ip', 'ping_task_state', 'create_date', 'update_date', 'childs'])

    def test_childs_field(self):
        data = self.serializer.data
        self.assertEqual(len(data['childs']), 1)
        self.assertEqual(data['childs'][0]['subnet'], '192.168.1.1')

    def test_read_only_fields(self):
        data = {'id': 999, 'create_date': '2023-01-01T00:00:00Z', 'update_date': '2023-01-01T00:00:00Z'}
        serializer = IPPrefixSerializer(instance=self.ip_prefix, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        serializer.save()
        self.ip_prefix.refresh_from_db()
        self.assertNotEqual(self.ip_prefix.id, 999)
        self.assertNotEqual(str(self.ip_prefix.create_date), '2023-01-01 00:00:00+00:00')
        self.assertNotEqual(str(self.ip_prefix.update_date), '2023-01-01 00:00:00+00:00')

    def test_serializer_with_invalid_data(self):
        invalid_data = {'ip': 'invalid_ip'}
        serializer = IPPrefixSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('ip', serializer.errors)

if __name__ == '__main__':
    unittest.main()
