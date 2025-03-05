from django.core.management.base import BaseCommand
import os

class Command(BaseCommand):
    help = 'Crea una nueva entidad en el archivo entities.py de una app Django'

    def add_arguments(self, parser):
        parser.add_argument('app_name', type=str, help='El nombre de la app')
        parser.add_argument('entity_name', type=str, help='El nombre de la entidad')
        parser.add_argument(
            '--subfolder', type=str, default='',
            help='Subcarpeta personalizada para alojar la estructura DDD'
        )

    def handle(self, *args, **options):
        app_name = options['app_name']
        entity_name = options['entity_name']
        subfolder = options['subfolder']
        
        base_path = os.path.join(subfolder, app_name) if subfolder else os.path.join('apps', app_name)
        entities_path = os.path.join(base_path, 'domain', 'entities.py')

        # Validar si el directorio existe
        if not os.path.exists(os.path.dirname(entities_path)):
            self.stderr.write(self.style.ERROR(f"No se encontró el módulo '{base_path}/domain/'."))
            return

        # Crear o actualizar el archivo entities.py
        if not os.path.exists(entities_path):
            with open(entities_path, 'w') as f:
                f.write("# Archivo de entidades\n\n")
        with open(entities_path, 'a') as f:
            f.write(f"""
                @dataclass
                class {entity_name}:
                    # TODO: Define los atributos de la entidad
                    def validate(self):
                        # TODO: Agrega validaciones específicas
                        pass
                """)
        self.stdout.write(self.style.SUCCESS(f"Entidad '{entity_name}' creada en {entities_path}"))
