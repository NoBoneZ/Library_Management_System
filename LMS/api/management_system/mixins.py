from .permissions import IsStaffOrReadOnly


class IsStaffOrReadOnlyMixins:
    permission_classes = [IsStaffOrReadOnly]
