import unittest
from unittest.mock import patch, MagicMock
from django.test import TestCase
from subnet_ip.tasks.ping_to_subnets_task import ping_to_subnets_task

class TestPingToSubnetsTask(TestCase):
    @patch('subnet_ip.tasks.ping_to_subnets_task.PingToSubnetsService')
    @patch('subnet_ip.tasks.ping_to_subnets_task.logger')
    def test_ping_to_subnets_task_success(self, mock_logger, mock_ping_service):
        result = ping_to_subnets_task('192.168.1.0/24')
        
        mock_ping_service.ping.assert_called_once_with('192.168.1.0/24')
        mock_logger.info.assert_any_call('ping_to_subnets_task started with args: (\'192.168.1.0/24\',)')
        mock_logger.info.assert_any_call('ping_to_subnets_task completed. ')
        self.assertTrue(result)

    @patch('subnet_ip.tasks.ping_to_subnets_task.PingToSubnetsService')
    @patch('subnet_ip.tasks.ping_to_subnets_task.logger')
    def test_ping_to_subnets_task_multiple_args(self, mock_logger, mock_ping_service):
        result = ping_to_subnets_task('192.168.1.0/24', '10.0.0.0/8')
        
        mock_ping_service.ping.assert_called_once_with('192.168.1.0/24', '10.0.0.0/8')
        mock_logger.info.assert_any_call('ping_to_subnets_task started with args: (\'192.168.1.0/24\', \'10.0.0.0/8\')')
        mock_logger.info.assert_any_call('ping_to_subnets_task completed. ')
        self.assertTrue(result)

    @patch('subnet_ip.tasks.ping_to_subnets_task.PingToSubnetsService')
    @patch('subnet_ip.tasks.ping_to_subnets_task.logger')
    def test_ping_to_subnets_task_with_kwargs(self, mock_logger, mock_ping_service):
        result = ping_to_subnets_task('192.168.1.0/24', timeout=5)
        
        mock_ping_service.ping.assert_called_once_with('192.168.1.0/24')
        mock_logger.info.assert_any_call('ping_to_subnets_task started with args: (\'192.168.1.0/24\',)')
        mock_logger.info.assert_any_call('ping_to_subnets_task completed. ')
        self.assertTrue(result)

    @patch('subnet_ip.tasks.ping_to_subnets_task.PingToSubnetsService')
    @patch('subnet_ip.tasks.ping_to_subnets_task.logger')
    def test_ping_to_subnets_task_no_args(self, mock_logger, mock_ping_service):
        result = ping_to_subnets_task()
        
        mock_ping_service.ping.assert_called_once_with()
        mock_logger.info.assert_any_call('ping_to_subnets_task started with args: ()')
        mock_logger.info.assert_any_call('ping_to_subnets_task completed. ')
        self.assertTrue(result)

    @patch('subnet_ip.tasks.ping_to_subnets_task.PingToSubnetsService')
    @patch('subnet_ip.tasks.ping_to_subnets_task.logger')
    def test_ping_to_subnets_task_exception(self, mock_logger, mock_ping_service):
        mock_ping_service.ping.side_effect = Exception("Test exception")
        
        with self.assertRaises(Exception):
            ping_to_subnets_task('192.168.1.0/24')
        
        mock_logger.info.assert_called_once_with('ping_to_subnets_task started with args: (\'192.168.1.0/24\',)')
        mock_logger.info.assert_not_called()  # The completion log should not be called due to the exception
