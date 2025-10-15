from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import UserPassesTestMixin

class RoleRequiredMixin(UserPassesTestMixin):
    """Миксин для проверки роли пользователя"""
    allowed_roles = []
    
    def test_func(self):
        user = self.request.user
        return user.is_authenticated and user.role in self.allowed_roles
    
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
    allowed_roles = ['accountant', 'deputy_director', 'director']

class HRRequiredMixin(RoleRequiredMixin):
    allowed_roles = ['hr', 'deputy_director', 'director']

class AdminRequiredMixin(RoleRequiredMixin):
    allowed_roles = ['admin', 'deputy_director', 'director']

class TraineeRequiredMixin(RoleRequiredMixin):
    allowed_roles = ['trainee', 'lawyer', 'advocate', 'manager', 'deputy_director', 'director']

class ExternalLawyerRequiredMixin(RoleRequiredMixin):
    allowed_roles = ['external_lawyer']

class OwnerRequiredMixin(UserPassesTestMixin):
    """Миксин для проверки, что пользователь является владельцем объекта"""
    def test_func(self):
        obj = self.get_object()
        user = self.request.user
        
        # Для дел - проверяем, является ли пользователь ответственным юристом
        if hasattr(obj, 'responsible_lawyer'):
            return user == obj.responsible_lawyer
        
        # Для клиентов - проверяем, является ли пользователь основным контактом
        if hasattr(obj, 'primary_contact'):
            return user == obj.primary_contact
        
        # Для документов - проверяем, является ли пользователь создателем
        if hasattr(obj, 'created_by'):
            return user == obj.created_by
        
        return False

class OwnerOrManagerMixin(UserPassesTestMixin):
    """Миксин для проверки, что пользователь является владельцем или менеджером"""
    def test_func(self):
        obj = self.get_object()
        user = self.request.user
        
        # Владелец имеет доступ
        if hasattr(obj, 'responsible_lawyer') and user == obj.responsible_lawyer:
            return True
        
        if hasattr(obj, 'primary_contact') and user == obj.primary_contact:
            return True
        
        if hasattr(obj, 'created_by') and user == obj.created_by:
            return True
        
        # Менеджеры и выше имеют доступ
        return user.role in ['manager', 'deputy_director', 'director']