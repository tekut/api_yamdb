from rest_framework import permissions


class IsAdminOrAuthor(permissions.BasePermission):
    message = 'You dont have the rights to perform this action'

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.is_admin
        )

    def has_object_permission(self, request, view, obj):
        return (
            obj == request.user
            or request.user.is_admin
        )


class IsAdmin(permissions.BasePermission):
    message = 'You dont have the Admin role'

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_admin
        )


class IsAdminOrAuthorOrModerator(permissions.BasePermission):
    message = 'Данный запрос недоступен для вас.'

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.user.is_admin
            or request.user.is_moderator
            or request.user == obj.author
        )
