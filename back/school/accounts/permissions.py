from rest_framework.permissions import BasePermission

class IsAdminRole(BasePermission):
    
    def has_permission(self, request, view):
        u = request.user
        return bool(u and u.is_authenticated and (getattr(u, "role", None) == "ADMIN" or u.is_superuser))

class IsManagerOrAdmin(BasePermission):
    
    def has_permission(self, request, view):
        u = request.user
        if not (u and u.is_authenticated):
            return False
        role = getattr(u, "role", None)
        return bool(role in ("MANAGER", "ADMIN") or u.is_superuser)