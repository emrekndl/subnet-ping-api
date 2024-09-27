import unittest
from unittest.mock import patch, MagicMock
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from netaddr import IPNetwork
from subnet_ip.models import IPPrefix
from subnet_ip.api.views import IPPrefixListCreateAPIView, IPPrefixDetailAPIView

class TestIPPrefixListCreateAPIView(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = '/api/ipprefix/'

    @patch('subnet_ip.api.views.ping_to_subnets_task')
    def test_create_valid_ipv4(self, mock_task):
        mock_task.apply_async.return_value.task_id = 'test_task_id'
        data = {'ip': '192.168.1.0/24'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(IPPrefix.objects.count(), 1)

    @patch('subnet_ip.api.views.ping_to_subnets_task')
    def test_create_invalid_ipv4_prefix(self, mock_task):
        data = {'ip': '192.168.1.0/16'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('subnet_ip.api.views.ping_to_subnets_task')
    def test_create_valid_ipv6(self, mock_task):
        mock_task.apply_async.return_value.task_id = 'test_task_id'
        data = {'ip': '2001:db8::/64'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    @patch('subnet_ip.api.views.ping_to_subnets_task')
    def test_create_invalid_ipv6_prefix(self, mock_task):
        data = {'ip': '2001:db8::/32'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('subnet_ip.api.views.ping_to_subnets_task')
    def test_create_duplicate_ip(self, mock_task):
        mock_task.apply_async.return_value.task_id = 'test_task_id'
        data = {'ip': '192.168.1.0/24'}
        self.client.post(self.url, data)
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class TestIPPrefixDetailAPIView(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.ip_prefix = IPPrefix.objects.create(ip='192.168.1.0/24', ping_task_state='SUCCESS')
        self.url = f'/api/ipprefix/{self.ip_prefix.id}/'

    @patch('subnet_ip.api.views.cache')
    def test_retrieve_ip_prefix(self, mock_cache):
        mock_cache.get.return_value = None
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['ip'], '192.168.1.0/24')

    @patch('subnet_ip.api.views.cache')
    def test_delete_ip_prefix(self, mock_cache):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(IPPrefix.objects.count(), 0)
        mock_cache.delete.assert_called_once_with(self.ip_prefix)

if __name__ == '__main__':
    unittest.main()
