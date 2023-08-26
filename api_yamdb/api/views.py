import uuid

from django.core.mail import send_mail
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets, status, mixins
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.pagination import LimitOffsetPagination

from reviews.models import Review, Title, Category, Genres
from api.filter import GenreFilter
from api.serializers import (TitlesSerializer,
                             TitlesPostSerializer,
                             CategoriesSerializer,
                             GenresSerializer,
                             SignUpSerializer,
                             UserSerializer,
                             CommentSerializer,
                             ReviewSerializer,
                             TokenSerializer,
                             NoRoleSerializer,
                             )
from api.permissions import (IsAdmin,
                             IsAdminOrAuthor,
                             IsAdminOrAuthorOrModerator,
                             AdminOrReadOnly,
                             )
from users.models import User


class CreateListDestroy(mixins.CreateModelMixin,
                        mixins.ListModelMixin,
                        mixins.DestroyModelMixin,
                        viewsets.GenericViewSet):
    pass


@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    serializer = SignUpSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.validated_data['email']
    username = serializer.validated_data['username']
    try:
        user, create = User.objects.get_or_create(
            username=username,
            email=email
        )
    except IntegrityError:
        return Response(
            'Пользователь с такими полями уже зарегистрирован',
            status=status.HTTP_400_BAD_REQUEST
        )
    confirmation_code = str(uuid.uuid4())
    user.confirmation_code = confirmation_code
    user.save()
    send_mail(
        'Код подверждения', confirmation_code,
        ['admin@email.com'], (email, ), fail_silently=False
    )
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def token(request):
    serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.validated_data['username']
    confirmation_code = serializer.validated_data['confirmation_code']
    userdata = get_object_or_404(User, username=username)
    if confirmation_code == userdata.confirmation_code:
        token = str(AccessToken.for_user(userdata))
        return Response({'token': token}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdminOrAuthor, )
    lookup_field = 'username'

    @action(
        methods=['get', 'patch'],
        detail=False,
        url_path='me',
        permission_classes=(IsAuthenticated, )
    )
    def me_patch(self, request):
        user = get_object_or_404(User, username=self.request.user)
        if request.method == 'GET':
            serializer = NoRoleSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        if request.method == 'PATCH':
            serializer = NoRoleSerializer(user, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)


class TitlesViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitlesSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,)
    filterset_class = GenreFilter
    search_fields = ('category__slug', 'genre__slug', 'name', 'year',)
    permission_classes = [AdminOrReadOnly]

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitlesSerializer
        return TitlesPostSerializer


class CategoriesViewSet(CreateListDestroy):
    queryset = Category.objects.all()
    serializer_class = CategoriesSerializer
    pagination_class = LimitOffsetPagination
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    permission_classes = [AdminOrReadOnly]


class GenresViewSet(CreateListDestroy):
    queryset = Genres.objects.all()
    serializer_class = GenresSerializer
    pagination_class = LimitOffsetPagination
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    permission_classes = [AdminOrReadOnly]


class ReviewViewSet(viewsets.ModelViewSet):
    """Вьюсет для отзывов."""
    serializer_class = ReviewSerializer
    permission_classes = (IsAdminOrAuthorOrModerator,)

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        reviews_id = self.kwargs.get('pk')
        title = get_object_or_404(Title, id=title_id)

        if not reviews_id:
            return title.reviews.all()
        return title.reviews.filter(id=reviews_id)

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        serializer.save(
            author=self.request.user,
            title=Title.objects.get(id=title_id),
        )


class CommentViewSet(viewsets.ModelViewSet):
    """Вьюсет для комментариев."""
    serializer_class = CommentSerializer
    permission_classes = (IsAdminOrAuthorOrModerator,)

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        reviews_id = self.kwargs.get('review_id')
        comment_id = self.kwargs.get('pk')
        title = get_object_or_404(Title, id=title_id)
        review = get_object_or_404(Review, id=reviews_id)

        if not comment_id:
            return review.comments.all()
        return review.comments.filter(id=comment_id)

    def perform_create(self, serializer):
        reviews_id = self.kwargs.get('review_id')
        serializer.save(
            author=self.request.user,
            title=Title.objects.get(id=reviews_id),
        )
