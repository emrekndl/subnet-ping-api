import unittest
from django.test import TestCase
from django.db import IntegrityError
from subnet_ip.models import IPPrefix, IPSubnets

class TestIPPrefix(TestCase):
    def test_ip_prefix_creation(self):
        ip_prefix = IPPrefix.objects.create(ip='192.168.1.0/24', ping_task_state='pending')
        self.assertEqual(ip_prefix.ip, '192.168.1.0/24')
        self.assertEqual(ip_prefix.ping_task_state, 'pending')

    def test_ip_prefix_unique_constraint(self):
        IPPrefix.objects.create(ip='10.0.0.0/8', ping_task_state='completed')
        with self.assertRaises(IntegrityError):
            IPPrefix.objects.create(ip='10.0.0.0/8', ping_task_state='pending')

    def test_ip_prefix_str_representation(self):
        ip_prefix = IPPrefix.objects.create(ip='172.16.0.0/16', ping_task_state='in_progress')
        self.assertEqual(str(ip_prefix), '172.16.0.0/16')

class TestIPSubnets(TestCase):
    def setUp(self):
        self.parent_ip = IPPrefix.objects.create(ip='192.168.0.0/16', ping_task_state='completed')

    def test_ip_subnet_creation(self):
        subnet = IPSubnets.objects.create(parent_ip=self.parent_ip, subnet='192.168.1.0/24')
        self.assertEqual(subnet.subnet, '192.168.1.0/24')
        self.assertFalse(subnet.status)

    def test_ip_subnet_str_representation(self):
        subnet = IPSubnets.objects.create(parent_ip=self.parent_ip, subnet='192.168.2.0/24')
        self.assertEqual(str(subnet), '192.168.2.0/24')

    def test_ip_subnet_parent_relationship(self):
        subnet = IPSubnets.objects.create(parent_ip=self.parent_ip, subnet='192.168.3.0/24')
        self.assertEqual(subnet.parent_ip, self.parent_ip)

    def test_ip_subnet_status_update(self):
        subnet = IPSubnets.objects.create(parent_ip=self.parent_ip, subnet='192.168.4.0/24')
        subnet.status = True
        subnet.save()
        updated_subnet = IPSubnets.objects.get(id=subnet.id)
        self.assertTrue(updated_subnet.status)
