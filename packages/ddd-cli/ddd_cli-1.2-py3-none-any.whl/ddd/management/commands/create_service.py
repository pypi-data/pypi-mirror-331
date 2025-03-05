from django.core.management.base import BaseCommand
import os

class Command(BaseCommand):
    help = 'Crea un nuevo servicio en el archivo services.py de una app Django'

    def add_arguments(self, parser):
        parser.add_argument('app_name', type=str, help='El nombre de la app')
        parser.add_argument('service_name', type=str, help='El nombre del servicio')
        parser.add_argument(
            '--subfolder', type=str, default='',
            help='Subcarpeta personalizada para alojar la estructura DDD'
        )

    def handle(self, *args, **options):
        app_name = options['app_name']
        service_name = options['service_name']
        subfolder = options['subfolder']

        base_path = os.path.join(subfolder, app_name) if subfolder else os.path.join('apps', app_name)
        services_path = os.path.join(base_path, 'domain', 'services.py')

        # Validar si el directorio existe
        if not os.path.exists(os.path.dirname(services_path)):
            self.stderr.write(self.style.ERROR(f"No se encontró el módulo '{base_path}/domain/'."))
            return

        # Crear o actualizar el archivo services.py
        if not os.path.exists(services_path):
            with open(services_path, 'w') as f:
                f.write("# Archivo de servicios\n\n")
        with open(services_path, 'a') as f:
            f.write(f"""
                def {service_name}(*args, **kwargs):
                    \"\"\"
                    Servicio para {service_name.replace('_', ' ')}.
                    \"\"\"
                    # TODO: Implementa la lógica de negocio
                    pass
            """)
        self.stdout.write(self.style.SUCCESS(f"Servicio '{service_name}' creado en {services_path}"))
