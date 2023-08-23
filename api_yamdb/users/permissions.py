from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    message = 'Only Admin is permitted'

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_admin
        )


class IsUserAdmin(permissions.BasePermission):
    message = 'You dont have the Admin role'

    def has_permission(self, request, view):
        return request.user.is_admin


class IsAdminOrAuthorOrModerator(permissions.BasePermission):
    """Даёт доступ неадмину/немодеру/неавтору только к GET/OPTIONS/HEAD."""

    message = 'Данный запрос недоступен для вас.'

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
            and (
                request.user.is_admin
                or request.user.is_moderator
                or request.user == obj.author
            )
        )
