from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsSelfLecturer(BasePermission):
    """
    Allows access only to the lecturer attached to the user.
    """
    def has_object_permission(self, request, view, obj):
        return hasattr(obj, 'user') and obj.user == request.user

class CanEditLecturerStatus(BasePermission):
    """
    Allows editing only the 'status' field, and only by the attached user or admin.
    """
    def has_object_permission(self, request, view, obj):
        # Only allow PATCH/PUT if only 'status' is being updated
        if request.method in ['PATCH', 'PUT']:
            allowed_fields = set(request.data.keys())
            return allowed_fields <= {'status'} and (obj.user == request.user or request.user.is_staff)
        return False

class IsOwnSchedule(BasePermission):
    """
    Allows viewing schedules only for the lecturer attached to the user.
    """
    def has_object_permission(self, request, view, obj):
        return obj.lecturer.user == request.user