from rest_framework import permissions

class IsUserOwner(permissions.BasePermission):
    """
    Checks if user is the owner of the object.
    Instances must have a method named 'user_is_owner'
    returning boolean permission.
    """

    def has_object_permission(self, request, view, obj):
        if obj is None:
            raise ValueError("'obj' cannot be None")
        
        if not hasattr(obj, 'user_is_owner'):
            raise ValueError("'obj' has no method 'user_is_owner'.")

        return obj.user_is_owner(request.user)