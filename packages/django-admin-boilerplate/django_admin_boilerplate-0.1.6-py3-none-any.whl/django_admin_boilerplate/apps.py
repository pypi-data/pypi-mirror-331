from django.apps import AppConfig

class DjangoAdminBoilerplateConfig(AppConfig):
    name = 'django_admin_boilerplate'

    def ready(self):
        import django_admin_boilerplate.management.commands
