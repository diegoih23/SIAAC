"""Permisos compartidos basados en roles del usuario SIAAC."""
from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdministrator(BasePermission):
    message = "Solo un administrador puede realizar esta acción."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_admin_role)


class IsOperatorOrAdmin(BasePermission):
    message = "Se requiere rol de operador o administrador."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in {"ADMIN", "OPERATOR"}
        )


class IsAdminOrReadOnly(BasePermission):
    """Lectura para cualquier usuario autenticado; escritura solo administradores."""

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.method in SAFE_METHODS:
            return True
        return request.user.role == "ADMIN"


class IsOperatorOrAdminOrReadOnly(BasePermission):
    """Lectura para todos; escritura para operadores y administradores."""

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.method in SAFE_METHODS:
            return True
        return request.user.role in {"ADMIN", "OPERATOR"}
