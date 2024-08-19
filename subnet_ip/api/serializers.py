from rest_framework import serializers
from subnet_ip.models import IPPrefix, IPSubnets


class IPSubnetsSerializer(serializers.ModelSerializer):
    """ Serializer for IPSubnets model """
 
    class Meta:
        model = IPSubnets
        fields = '__all__'
        read_only_fields = 'id', 'create_date', 'update_date'


class IPPrefixSerializer(serializers.ModelSerializer):
    """ IP Address Serializer """

    childs = IPSubnetsSerializer(many=True, read_only=True)

    class Meta:
        model = IPPrefix
        fields = '__all__'
        read_only_fields = 'id', 'create_date', 'update_date'
