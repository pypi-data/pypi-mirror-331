import os
import shutil
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Copy the django_admin_boilerplate app to the current Django project"

    def handle(self, *args, **kwargs):
        package_root = os.path.dirname(os.path.abspath(__file__))
        # print("package_root:  ", package_root, "\n")
        app_src = os.path.join(package_root, "..", "..", "..", "django_admin_boilerplate")
        # print("app_src:  ", app_src, "\n")
        project_root = os.getcwd()
        app_dest = os.path.join(project_root, "django_admin_boilerplate")
        # print("app_dest:  ", app_dest, "\n")
        if os.path.exists(app_dest):
            self.stdout.write(self.style.WARNING("Skipping copy: 'django_admin_boilerplate' already exists."))
        else:
            shutil.copytree(app_src, app_dest)
            self.stdout.write(self.style.SUCCESS(f"Successfully copied 'django_admin_boilerplate' to {project_root}"))
