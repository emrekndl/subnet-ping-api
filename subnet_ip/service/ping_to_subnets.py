import os
import logging

from netaddr import IPNetwork
from subnet_ip.models import IPSubnets, IPPrefix

logger = logging.getLogger(__name__)


class PingToSubnetsService():
    """ Ping Subnets Service """

    @staticmethod
    def ping(*args):
        """ Pinging Method for All Subnets """
        
        subnet_list = {1: [], 0: []}
        ip = IPNetwork(args[0])
        
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
            p_ip = IPPrefix.objects.get(ip=args[0])

            for k, v in subnet_list.items():
                for i in v:
                    obj, _ = IPSubnets.objects.update_or_create(
                        parent_ip=p_ip,
                        subnet=i,
                        status=k
                    )
                    obj.save()

            p_ip.ping_task_state = 'SUCCESS'
            p_ip.save()
            logger.info("Successfully pinged.")
        except IPPrefix.DoesNotExist:
            logger.error(f"IPPrefix object does not exist for {args[0]}")
