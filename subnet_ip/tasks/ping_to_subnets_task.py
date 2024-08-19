import logging
from celery import shared_task


logger = logging.getLogger(__name__)


@shared_task(name='ping_to_subnets_task', queue='queue1')
def ping_to_subnets_task(*args, **kwargs):
    """ Pinging Task for All Subnets """
    
    logger.info(f'ping_to_subnets_task started with args: {args}')

    from subnet_ip.service.ping_to_subnets import PingToSubnetsService
    PingToSubnetsService.ping(*args)

    logger.info(f'ping_to_subnets_task completed. ')

    return True
