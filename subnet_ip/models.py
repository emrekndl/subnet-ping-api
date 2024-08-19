from django.db import models


class IPPrefix(models.Model):
    """
    IP Prefix Model
    192.168.154.255/24 - ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff/64
    """

    ip = models.CharField(max_length=42, unique=True)
    ping_task_state = models.CharField(max_length=15)
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'IP Address'
        ordering = ['-ip']

    def __str__(self):
        return str(self.ip)


class IPSubnets(models.Model):
    """ Subnets Model """
    parent_ip = models.ForeignKey(IPPrefix, on_delete=models.CASCADE,
                                  related_name='childs')
    subnet = models.CharField(max_length=42, blank=True, null=True)
    status = models.BooleanField(default=False)
    # status = models.CharField(max_length=15, blank=True, null=True)
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'IP Subnets'

    def __str__(self):
       return str(self.subnet)
