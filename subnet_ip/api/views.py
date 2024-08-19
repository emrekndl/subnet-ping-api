from subnet_ip.models import IPPrefix, IPSubnets
from subnet_ip.api.serializers import IPPrefixSerializer, IPSubnetsSerializer
from subnet_ip.tasks import ping_to_subnets_task
from celery.result import AsyncResult

from rest_framework import generics, mixins
from rest_framework import status
from rest_framework.response import Response

from netaddr import IPNetwork
from django.core.cache import cache
from django.http import QueryDict 
from django.conf import settings


CACHE_TTL = getattr(settings, 'CACHE_TTL')
IPV4 = getattr(settings, 'IPV4')
IPV6 = getattr(settings, 'IPV6')
IPV4_PREFIXLEN = getattr(settings, 'IPV4_PREFIXLEN')
IPV6_PREFIXLEN = getattr(settings, 'IPV6_PREFIXLEN')
IPV6_PREFIXLEN_2 = getattr(settings, 'IPV6_PREFIXLEN_2')


class IPPrefixListCreateAPIView(generics.ListCreateAPIView):
    """ IP Prefix List and Create API View """

    queryset = IPPrefix.objects.all()
    serializer_class = IPPrefixSerializer

    def create(self, request, *args, **kwargs):
        ip_addr = request.data['ip']
        try:
            ip = IPNetwork(str(ip_addr))

            if (ip.version == IPV4 and ip._prefixlen < IPV4_PREFIXLEN) or \
               (ip.version == IPV6 and ip._prefixlen < IPV6_PREFIXLEN):

                return Response({"error": f"IP address ipv4 for prefix >= \
                    /{IPV4_PREFIXLEN} and ipv6 for prefix >= \
                    {IPV6_PREFIXLEN}"}, status=status.HTTP_400_BAD_REQUEST)

            if ip.version == IPV6:
                usableaddr = 2**(128 - ip._prefixlen)
                if ip._prefixlen < IPV6_PREFIXLEN_2:
                    return Response({"error": f"IP subnet calculating for \
                        this prefix take to long time calculating. \
                            ipv6 prefix {ip._prefixlen} usable address: \
                                {usableaddr}"},
                                    status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": "Invalid IP address", "e": f"{e}"},
                            status=status.HTTP_400_BAD_REQUEST)

        if isinstance(request.data, QueryDict):
            request.data._mutable = True

        if ip_old := IPPrefix.objects.filter(ip=ip_addr):
            # second same ip post request
            if ip_old[0].ping_task_state != 'PENDING':
                # second same ip post request when task is not complate.
                task_state = self.ping_to_hosts(str(ip_addr))
                cache.delete(ip_old[0])
                ip_old[0].ping_task_state = task_state
                ip_old[0].save()
                serializer = IPPrefixSerializer(ip_old[0])
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response({"error": "Task in 'PENDING' state. \
                Please Waiting!"},
                            status=status.HTTP_400_BAD_REQUEST)

        task_state = self.ping_to_hosts(str(ip_addr))

        # new ping_task state
        request.data.update({'ping_task_state': task_state})
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED, headers=headers)

    def ping_to_hosts(self, ip):
        return AsyncResult(ping_to_subnets_task.apply_async(
            args=[ip]).task_id).state


class IPPrefixDetailAPIView(generics.RetrieveUpdateDestroyAPIView, mixins.ListModelMixin):
    """ IP Prefix Detail API View """

    queryset = IPPrefix.objects.all()
    serializer_class = IPPrefixSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        cache_data = cache.get(instance)
        if cache_data is None:
            cache_data = serializer.data
            cache.set(f"{instance}", cache_data, CACHE_TTL)
        return Response(cache_data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        cache.delete(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)



class IPSubnetsListCreateAPIView(generics.ListCreateAPIView):
    queryset = IPSubnets.objects.all()
    serializer_class = IPSubnetsSerializer


class IPSubnetsDetailAPIView(generics.RetrieveDestroyAPIView):
    queryset = IPSubnets.objects.all()
    serializer_class = IPSubnetsSerializer
