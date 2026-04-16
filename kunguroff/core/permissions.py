from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import UserPassesTestMixin


class RoleRequiredMixin(UserPassesTestMixin):
    """Миксин для проверки роли пользователя. Суперпользователь проходит всегда."""
    allowed_roles = []

    def test_func(self):
        user = self.request.user
        if not user.is_authenticated:
            return False
        if user.is_superuser:
            return True
        return user.role in self.allowed_roles

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            raise PermissionDenied("У вас недостаточно прав для доступа к этой странице")
        return super().handle_no_permission()


# Конкретные миксины для различных ролей
class DirectorRequiredMixin(RoleRequiredMixin):
    allowed_roles = ['director']

class DeputyDirectorRequiredMixin(RoleRequiredMixin):
    allowed_roles = ['deputy_director', 'director']

class ManagerRequiredMixin(RoleRequiredMixin):
    allowed_roles = ['manager', 'deputy_director', 'director']

class LawyerRequiredMixin(RoleRequiredMixin):
    allowed_roles = ['lawyer', 'advocate', 'manager', 'deputy_director', 'director']

class AccountantRequiredMixin(RoleRequiredMixin):
    allowed_roles = ['accountant', 'manager', 'deputy_director', 'director']

class HRRequiredMixin(RoleRequiredMixin):
    allowed_roles = ['hr', 'deputy_director', 'director']

class AdminRequiredMixin(RoleRequiredMixin):
    allowed_roles = ['admin', 'deputy_director', 'director']

class TraineeRequiredMixin(RoleRequiredMixin):
    allowed_roles = ['trainee', 'lawyer', 'advocate', 'manager', 'deputy_director', 'director']

class ExternalLawyerRequiredMixin(RoleRequiredMixin):
    allowed_roles = ['external_lawyer']


class OwnerRequiredMixin(UserPassesTestMixin):
    """Суперпользователь имеет доступ ко всему."""
    def test_func(self):
        user = self.request.user
        if not user.is_authenticated:
            return False
        if user.is_superuser:
            return True

        obj = self.get_object()

        if hasattr(obj, 'responsible_lawyer'):
            return user == obj.responsible_lawyer
        if hasattr(obj, 'primary_contact'):
            return user == obj.primary_contact
        if hasattr(obj, 'created_by'):
            return user == obj.created_by

        return False


class OwnerOrManagerMixin(UserPassesTestMixin):
    """Суперпользователь имеет доступ ко всему."""
    def test_func(self):
        user = self.request.user
        if not user.is_authenticated:
            return False
        if user.is_superuser:
            return True

        obj = self.get_object()

        if hasattr(obj, 'responsible_lawyer') and user in obj.responsible_lawyer.all():
            return True
        if hasattr(obj, 'primary_contact') and user == obj.primary_contact:
            return True
        if hasattr(obj, 'created_by') and user == obj.created_by:
            return True

        return user.role in ['manager', 'deputy_director', 'director']
