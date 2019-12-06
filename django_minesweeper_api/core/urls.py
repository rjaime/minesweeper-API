from rest_framework import routers

from . import views


router = routers.SimpleRouter()

router.register(r'matches',
    views.MatchViewSet,
    base_name='matches'
)

urlpatterns = [
    *router.urls,
]