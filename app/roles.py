from rest_framework_roles.roles import is_anon, is_user, is_admin, is_staff
from lecturers.models import Lecturer


def is_self_lecturer(request, view, pk=None):
    # For custom actions, check for lecturer_id
    if 'lecturer_id' in getattr(view, 'kwargs', {}):
        lecturer_id = view.kwargs['lecturer_id']
        from lecturers.models import Lecturer
        try:
            lecturer = Lecturer.objects.get(pk=lecturer_id)
        except Lecturer.DoesNotExist:
            return False
        return is_user(request, view) and lecturer.user == request.user
    # For standard retrieve/update/destroy with pk
    if 'pk' in getattr(view, 'kwargs', {}):
        obj = view.get_object()
        lecturer = getattr(obj, 'lecturer', None)
        if lecturer is not None and hasattr(lecturer, 'user'):
            return is_user(request, view) and lecturer.user == request.user
        if hasattr(obj, 'user'):
            return is_user(request, view) and obj.user == request.user
        return False
    return False
ROLES = {
    # Django vanilla roles
    'anon': is_anon,
    'user': is_user,
    'admin': is_admin,
    'staff': is_staff,

    # Some custom role examples
    'lecturer': 
        lambda request, view: 
            is_user(request, view) 
            and request.user.groups.filter(name='lecturer').exists(),
    'potential_lecturer': 
        lambda request, view: 
            is_user(request, view) 
            and request.user.groups.filter(name='potential_lecturer').exists(),
    'it_faculty': 
        lambda request, view: 
            is_user(request, view) 
            and request.user.groups.filter(name='it_faculty').exists(),
    'education_department': 
        lambda request, view: 
            is_user(request, view) 
            and request.user.groups.filter(name='education_department').exists(),
    'supervision_department':
        lambda request, view: 
            is_user(request, view) 
            and request.user.groups.filter(name='supervision_department').exists(),
}