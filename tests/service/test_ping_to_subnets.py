import unittest
from unittest.mock import patch, MagicMock
from django.test import TestCase
from netaddr import IPNetwork
from subnet_ip.models import IPPrefix, IPSubnets
from subnet_ip.service.ping_to_subnets import PingToSubnetsService

class TestPingToSubnetsService(TestCase):
    def setUp(self):
        self.ip_prefix = IPPrefix.objects.create(ip='192.168.1.0/30', ping_task_state='PENDING')

    @patch('subnet_ip.service.ping_to_subnets.os.system')
    def test_ping_ipv4_success(self, mock_system):
        mock_system.side_effect = [0, 0, 0, 0]  # All IPs are active
        PingToSubnetsService.ping('192.168.1.0/30')

        self.ip_prefix.refresh_from_db()
        self.assertEqual(self.ip_prefix.ping_task_state, 'SUCCESS')
        self.assertEqual(IPSubnets.objects.filter(parent_ip=self.ip_prefix, status=1).count(), 4)
        self.assertEqual(IPSubnets.objects.filter(parent_ip=self.ip_prefix, status=0).count(), 0)

    @patch('subnet_ip.service.ping_to_subnets.os.system')
    def test_ping_ipv4_mixed_results(self, mock_system):
        mock_system.side_effect = [0, 1, 0, 1]  # Alternating active and inactive IPs
        PingToSubnetsService.ping('192.168.1.0/30')

        self.ip_prefix.refresh_from_db()
        self.assertEqual(self.ip_prefix.ping_task_state, 'SUCCESS')
        self.assertEqual(IPSubnets.objects.filter(parent_ip=self.ip_prefix, status=1).count(), 2)
        self.assertEqual(IPSubnets.objects.filter(parent_ip=self.ip_prefix, status=0).count(), 2)

    @patch('subnet_ip.service.ping_to_subnets.os.system')
    def test_ping_ipv6(self, mock_system):
        mock_system.return_value = 0  # All IPs are active
        ipv6_prefix = IPPrefix.objects.create(ip='2001:db8::/126', ping_task_state='PENDING')
        PingToSubnetsService.ping('2001:db8::/126')

        ipv6_prefix.refresh_from_db()
        self.assertEqual(ipv6_prefix.ping_task_state, 'SUCCESS')
        self.assertEqual(IPSubnets.objects.filter(parent_ip=ipv6_prefix, status=1).count(), 4)

    @patch('subnet_ip.service.ping_to_subnets.os.system')
    def test_ping_non_existent_ip_prefix(self, mock_system):
        mock_system.return_value = 0
        with self.assertLogs('subnet_ip.service.ping_to_subnets', level='ERROR') as cm:
            PingToSubnetsService.ping('10.0.0.0/30')
        self.assertIn("IPPrefix object does not exist for 10.0.0.0/30", cm.output[0])

    @patch('subnet_ip.service.ping_to_subnets.os.system')
    def test_ping_update_existing_subnets(self, mock_system):
        mock_system.side_effect = [0, 1, 0, 1]
        IPSubnets.objects.create(parent_ip=self.ip_prefix, subnet='192.168.1.0', status=0)
        IPSubnets.objects.create(parent_ip=self.ip_prefix, subnet='192.168.1.1', status=1)
        
        PingToSubnetsService.ping('192.168.1.0/30')

        self.assertEqual(IPSubnets.objects.get(parent_ip=self.ip_prefix, subnet='192.168.1.0').status, 1)
        self.assertEqual(IPSubnets.objects.get(parent_ip=self.ip_prefix, subnet='192.168.1.1').status, 0)

    @patch('subnet_ip.service.ping_to_subnets.os.system')
    @patch('subnet_ip.service.ping_to_subnets.logger')
    def test_ping_logging(self, mock_logger, mock_system):
        mock_system.return_value = 0
        PingToSubnetsService.ping('192.168.1.0/30')

        mock_logger.info.assert_any_call("active ip address: 192.168.1.0")
        mock_logger.info.assert_any_call("active ip address: 192.168.1.1")
        mock_logger.info.assert_any_call("active ip address: 192.168.1.2")
        mock_logger.info.assert_any_call("active ip address: 192.168.1.3")
        mock_logger.info.assert_called_with("Successfully pinged.")
