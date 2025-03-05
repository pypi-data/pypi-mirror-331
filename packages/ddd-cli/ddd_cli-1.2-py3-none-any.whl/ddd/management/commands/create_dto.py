from django.core.management.base import BaseCommand
import os

class Command(BaseCommand):
    help = 'Crea un archivo dtos.py o agrega una clase DTO a una app Django'

    def add_arguments(self, parser):
        parser.add_argument('app_name', type=str, help='El nombre de la app')
        parser.add_argument('dto_name', type=str, help='El nombre del DTO')
        parser.add_argument(
            '--subfolder', type=str, default='',
            help='Subcarpeta personalizada para alojar la estructura DDD'
        )

    def handle(self, *args, **options):
        app_name = options['app_name']
        dto_name = options['dto_name']
        subfolder = options['subfolder']

        base_path = os.path.join(subfolder, app_name) if subfolder else os.path.join('apps', app_name)
        dtos_path = os.path.join(base_path, 'domain', 'dtos.py')

        # Validar si el directorio existe
        if not os.path.exists(os.path.dirname(dtos_path)):
            self.stderr.write(self.style.ERROR(f"No se encontró el módulo '{base_path}/domain/'."))
            return

        # Crear o actualizar el archivo dtos.py
        if not os.path.exists(dtos_path):
            with open(dtos_path, 'w') as f:
                f.write("# Archivo de DTOs\n\n")
        with open(dtos_path, 'a') as f:
            f.write(f"""
                @dataclass
                class {dto_name}:
                    # TODO: Define los atributos del DTO
                    pass
            """)
        self.stdout.write(self.style.SUCCESS(f"DTO '{dto_name}' creado en {dtos_path}"))
