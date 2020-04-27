from django.conf.urls import url
from django.contrib import admin

from .views import HomeView, get_data, ChartData


urlpatterns = [
    url(r'^$', HomeView.as_view(), name='home'),
    url(r'^api/data/$', get_data, name='api-data'),
    url(r'^api/chart/data/$', ChartData.as_view()),
    url(r'^admin/', admin.site.urls),

]