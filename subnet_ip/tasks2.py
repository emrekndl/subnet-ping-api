import os
import logging

from celery import shared_task
from netaddr import IPNetwork
from .models import IPSubnets, IPPrefix


logging.basicConfig(filename='./task_log.txt', level=logging.INFO)


@shared_task(queue='queue1')
def ping_to_subnet_task(ip_str):
    """ Pinging Method for All Subnets """

    subnet_list = {1: [], 0: []}
    ip = IPNetwork(ip_str)

    logger = logging.getLogger(__name__)
    logger.info(f"""
        ip network : {ip.network}
        ip broadcast : {ip.broadcast}
        ip version : {ip.version}
        ip netmask : {ip.netmask}
        ip prefixlen : {ip.prefixlen}
        ip hostmask : {ip.hostmask}\n""")

    # generator for ipv6 subnets taking too long time calculating
    for i in iter(ip):
        resp = os.system(f"ping -c 1 -w 1 {str(i)} >/dev/null")
        if resp == 0:
            logger.info(f"active ip address: {str(i)}")
            subnet_list[1].append(str(i))
        else:
            logger.info(f"inactive ip address: {str(i)}")
            subnet_list[0].append(str(i))

    try:
        p_ip = IPPrefix.objects.get(ip=ip_str)

        for k, v in subnet_list.items():
            for i in v:
                obj, created = IPSubnets.objects.update_or_create(
                    parent_ip=p_ip,
                    subnet=i,
                    status=k
                )
                obj.save()

        p_ip.ping_task_state = 'SUCCESS'
        p_ip.save()
    except IPPrefix.DoesNotExist:
        logger.error(f"IPPrefix object does not exist for {ip_str}")
