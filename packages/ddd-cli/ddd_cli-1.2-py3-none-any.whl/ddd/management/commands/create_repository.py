from django.core.management.base import BaseCommand
import os

class Command(BaseCommand):
    help = 'Crea un archivo repository.py en una app Django'

    def add_arguments(self, parser):
        parser.add_argument('app_name', type=str, help='El nombre de la app')
        parser.add_argument(
            '--subfolder', type=str, default='',
            help='Subcarpeta personalizada para alojar la estructura DDD'
        )
        parser.add_argument(
            '--include-crud', action='store_true',
            help='Genera métodos CRUD (create, read, update, delete) en el repositorio'
        )

    def handle(self, *args, **options):
        app_name = options['app_name']
        subfolder = options['subfolder']
        include_crud = options['include_crud']

        base_path = os.path.join(subfolder, app_name) if subfolder else os.path.join('apps', app_name)
        repository_path = os.path.join(base_path, 'infrastructure', 'repository.py')

        # Validar si el directorio existe
        if not os.path.exists(os.path.dirname(repository_path)):
            self.stderr.write(self.style.ERROR(f"No se encontró el módulo '{base_path}/infrastructure/'."))
            return

        # Crear el archivo repository.py si no existe
        if not os.path.exists(repository_path):
            with open(repository_path, 'w') as f:
                f.write("# Archivo de repositorio\n\n")
                f.write(f"class {app_name.capitalize()}Repository:\n    pass\n")

        # Agregar métodos CRUD si --include-crud está habilitado
        if include_crud:
            with open(repository_path, 'a') as f:
                f.write("""
                    @staticmethod
                    def create(data):
                        # TODO: Implementa la lógica para crear un registro
                        pass

                    @staticmethod
                    def read(id):
                        # TODO: Implementa la lógica para leer un registro
                        pass

                    @staticmethod
                    def update(id, data):
                        # TODO: Implementa la lógica para actualizar un registro
                        pass

                    @staticmethod
                    def delete(id):
                        # TODO: Implementa la lógica para eliminar un registro
                        pass
                """)
        self.stdout.write(self.style.SUCCESS(f"Archivo 'repository.py' creado en {repository_path}"))
