from django.http import JsonResponse
from django.shortcuts import render
from django.core.cache import cache
# Create your views here.
from django.views import View

from apps.areas.models import Area


class AreasView(View):
    def get(self,request):

        parent_id = request.GET.get('area_id')
        if parent_id is None:
            cache_pro = cache.get('pro')
            if cache_pro is None:
                parent = Area.objects.filter(parent=None)
                cache_pro=[]
                for area in parent:
                    cache_pro.append({
                        "id":area.id,
                        "name":area.name
                    })
                cache.set('pro',cache_pro,3600)
            return JsonResponse({"code":0,"province_list":cache_pro})
        else:
            cache_pro = cache.get(parent_id)
            if cache_pro is None:
                city = Area.objects.filter(parent_id=parent_id)
                cache_pro = []
                for c in city:
                    cache_pro.append({
                        "id":c.id,
                        "name":c.name
                    })
                cache.set(parent_id,cache_pro,3600)
            return JsonResponse({"code":0,"subs":cache_pro})