from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (CategoriesViewSet, CommentViewSet, GenresViewSet,
                       ReviewViewSet, TitlesViewSet, UserViewSet, signup,
                       token)

router_v1 = DefaultRouter()
router_v1.register('users', UserViewSet)
router_v1.register(r'titles', TitlesViewSet)
router_v1.register(r'genres', GenresViewSet)
router_v1.register(r'categories', CategoriesViewSet)
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='reviews',
)
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments',
)

auth_patterns = [
    path('signup/', signup),
    path('token/', token),
]

urlpatterns = [
    path('v1/', include(router_v1.urls)),
    path('v1/auth/', include(auth_patterns)),
]
