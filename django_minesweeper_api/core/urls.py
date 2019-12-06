from django.conf.urls import url, include
from django.views.generic import TemplateView
from rest_framework import routers

from . import views


router = routers.SimpleRouter()

router.register(r'matches',
    views.MatchViewSet,
    base_name='matches'
)

api_urls = [
    url(r'^api/', include(router.urls)),
]

urlpatterns = [
    *api_urls,
    url(r'^$', TemplateView.as_view(template_name="lobby.html"), name='lobby'),
    url(r'^match/(?P<match_id>[0-9]+)/$', TemplateView.as_view(template_name="game.html"), name='match_game'),
]