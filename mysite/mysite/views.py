from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import View

from rest_framework.views import APIView
from rest_framework.response import Response
from . import test
from . import main
import os.path
import time

class HomeView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'charts.html', {"customers": 10})



def get_data(request, *args, **kwargs):
    data = {
        "sales": 100,
        "customers": 10,
    }
    return JsonResponse(data) # http response


class ChartData(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, format=None):
        data = main.main()
        return Response(data)
        # file_path='../static/outputs/Graph27.png'

        # while not os.path.exists(file_path):
        #     time.sleep(1)
        #
        # if os.path.isfile(file_path):
        #     return Response(data)
        # else:
        #     raise ValueError("%s isn't a file!" % file_path)


