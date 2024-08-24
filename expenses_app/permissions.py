from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.payer == request.user


# class IsSelfOrReadOnly(permissions.BasePermission):
#     def has_object_permission(self, request, view, obj):
#         # SAFE_METHODS are GET, HEAD or OPTIONS requests.
#         if request.method in permissions.SAFE_METHODS:
#             return True
#         return obj == request.user


# class UserViewSet(viewsets.ModelViewSet):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer
#     permission_classes = [permissions.IsAuthenticated, IsSelfOrReadOnly]

#     def get_queryset(self):
#         return User.objects.filter(id=self.request.user.id)
