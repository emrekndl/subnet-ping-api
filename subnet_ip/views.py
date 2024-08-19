from django.shortcuts import render, redirect
from django.utils.dateparse import parse_datetime
from django.conf import settings
from django.http import HttpResponse

import requests
import os
from .models import IPPrefix, IPSubnets

URL = settings.URL


def index(request):
    if request.method == "POST":
        new_ip = request.POST['ip']
        if new_ip != '':
            data = {
                "ip": new_ip 
            }
            r = requests.post(f"{URL}/api/ip/", data=data)

            if r.status_code in [201, 200]:
                return redirect('/')
            r = r.json()
            data  = IPPrefix.objects.all()
            return render(request, 'index.html', {'error': r, 'ip_list': data})

    # res = requests.get(f"{URL}/api/ip/")
    # data = res.json()
    data = IPPrefix.objects.all()
    # for i in data:
        # i = date_parse(i)
    return render(request, 'index.html', {'ip_list': data})


def subnet(request, pk):
    if request.method == "GET":
        # res = requests.get(f"{URL}/api/ip/prefix/{pk}")
        # data = res.json()
        # data = date_parse(data)
        data = IPSubnets.objects.filter(parent_ip=pk)
        return render(request, "subnet.html", {'data': data})


def ip_state_check(request, pk):
    if request.method == "GET":
        ip = IPPrefix.objects.get(pk=pk)
        if ip.ping_task_state == "PENDING":
            return HttpResponse("Task is still pending...", status=400)
        context = {
            "state": ip.ping_task_state, 
            "updated": ip.update_date
        } 
        return render(request, "partials/task_state.html", {'ip': context}) 

# def delete_ip(request, pk):
#     res = requests.delete(f"{URL}/api/ip/prefix/{pk}")
#     res = requests.get(f"{URL}/api/ip/")
#     data = res.json()
#     for i in data:
#         i = date_parse(i)
#     return render(request, 'index.html', {'ip_list': data})

def date_parse(data):
    data["update_date"] = parse_datetime(data["update_date"])
    data["create_date"] = parse_datetime(data["create_date"])
    for i in data["childs"]:
        i["update_date"] = parse_datetime(i["update_date"])
        i["create_date"] = parse_datetime(i["create_date"])
    return data
