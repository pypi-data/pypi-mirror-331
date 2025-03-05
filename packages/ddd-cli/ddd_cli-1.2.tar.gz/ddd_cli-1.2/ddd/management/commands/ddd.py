from django.core.management.base import BaseCommand, CommandError
import os
from jinja2 import Template

class Command(BaseCommand):
    help = "Comandos relacionados con la estructura DDD"


    def add_arguments(self, parser):
        subcommands = parser.add_subparsers(dest='subcommand', help='Subcomandos disponibles')

        # Subcomando: create-entity
        entity_parser = subcommands.add_parser('create-entity', help='Crea una nueva entidad')
        entity_parser.add_argument('app_path', type=str, help='El path relativo de la app dentro del proyecto (por ejemplo, "apps/app1")')
        entity_parser.add_argument('entity_name', type=str, help='El nombre de la entidad')
        entity_parser.add_argument(
            '--split', action='store_true', help='Crea un archivo separado para esta entidad'
        )

        # Subcomando: create-service
        service_parser = subcommands.add_parser('create-service', help='Crea un nuevo servicio')
        service_parser.add_argument('app_path', type=str, help='El path relativo de la app dentro del proyecto (por ejemplo, "apps/app1")')
        service_parser.add_argument('service_name', type=str, help='El nombre del servicio')  
        service_parser.add_argument('entity_name', type=str, help='El nombre de la entidad')        
        service_parser.add_argument(
            '--class-format', action='store_true', help='Crea un archivo con formato de clase'
        )          
        service_parser.add_argument(
            '--include-crud', action='store_true', help='Incluye métodos CRUD en el servicio'
        )        
        service_parser.add_argument(
            '--split', action='store_true', help='Crea un archivo separado para este servicio'
        )

        # Subcomando: create-repository
        repo_parser = subcommands.add_parser('create-repository', help='Crea un nuevo repositorio')
        repo_parser.add_argument('app_path', type=str, help='El path relativo de la app dentro del proyecto (por ejemplo, "apps/app1")')
        repo_parser.add_argument('entity_name', type=str, help='El nombre de la entidad')
        repo_parser.add_argument(
            '--include-crud', action='store_true', help='Incluye métodos CRUD en el repositorio'
        )

        # Subcomando: create-dto
        dto_parser = subcommands.add_parser('create-dto', help='Crea un nuevo DTO')
        dto_parser.add_argument('app_path', type=str, help='El path relativo de la app dentro del proyecto (por ejemplo, "apps/app1")')
        dto_parser.add_argument('dto_name', type=str, help='El nombre del DTO')
        dto_parser.add_argument(
            '--split', action='store_true', help='Crea un archivo separado para este DTO'
        )

        # Subcomando: create-view-api-apiview
        view_api_apiview_parser = subcommands.add_parser('create-view-api-apiview', help='Crea una view para api basada en ApiView')
        view_api_apiview_parser.add_argument('app_path', type=str, help='El path relativo de la app dentro del proyecto (por ejemplo, "apps/app1")')
        view_api_apiview_parser.add_argument('entity_name', type=str, help='El nombre de la entidad')

        # Subcomando: create-view-api-viewset
        view_api_apiviewset_parser = subcommands.add_parser('create-view-api-viewset', help='Crea una view para api basada en ViewSet')
        view_api_apiviewset_parser.add_argument('app_path', type=str, help='El path relativo de la app dentro del proyecto (por ejemplo, "apps/app1")')
        view_api_apiviewset_parser.add_argument('entity_name', type=str, help='El nombre de la entidad')

        # Subcomando: create-view
        view_web_parser = subcommands.add_parser('create-view', help='Crea una view para web')
        view_web_parser.add_argument('app_path', type=str, help='El path relativo de la app dentro del proyecto (por ejemplo, "apps/app1")')
        view_web_parser.add_argument('entity_name', type=str, help='El nombre de la entidad')


    def handle(self, *args, **options):
        subcommand = options.pop('subcommand', None)

        if not subcommand:
            self.stderr.write(self.style.ERROR("Debes especificar un subcomando. Usa '--help' para más detalles."))
            return

        if subcommand == 'create-entity':
            self.create_entity(**options)
        elif subcommand == 'create-service':
            self.create_service(**options)
        elif subcommand == 'create-repository':
            self.create_repository(**options)
        elif subcommand == 'create-dto':
            self.create_dto(**options)
        elif subcommand == 'create-view-api-apiview':
            self.create_view_api_apiview(**options)
        elif subcommand == 'create-view-api-viewset':
            self.create_view_api_viewset(**options)
        elif subcommand == 'create-view':
            self.create_view(**options)
        else:
            raise CommandError(f"Subcomando '{subcommand}' no reconocido.")
        

    def _renderTemplate(self, templateName: str, fileName:str, render_params: dict) -> str:
        '''
        return content
        '''

        # Construir la ruta absoluta de la plantilla
        templates_dir = os.path.join(os.path.dirname(__file__), '..', 'templates', templateName)
        templates_dir = os.path.normpath(templates_dir)  # Normalizar la ruta 

        # Cargar la plantilla imports
        template_imports = os.path.join(templates_dir, fileName)
        with open(template_imports, 'r') as template_file:
            template_content = template_file.read()

        # Renderizar la plantilla imports
        return Template(template_content).render(**render_params)
    

    def __create__init__file(self, path):
        """Crea un archivo __init__.py en el directorio especificado"""
        with open(os.path.join(path, '__init__.py'), 'w') as f:
            pass


    def __create__init__files(self, path):
        """Crea un archivo __init__.py en el directorio especificado 
        y en todos los directorios padres hasta el directorio raíz 
        o hasta encontrar un archivo __init__.py"""
        while True:
            if os.path.exists(os.path.join(path, '__init__.py')):
                break
            self.__create__init__file(path)
            path = os.path.dirname(path)
            if path == '' or path == '/':
                break


    def create_entity(self, app_path, entity_name, split=False, **kwargs):
        """Crea una nueva entidad"""
        entities_dir = os.path.join(app_path, 'domain') if not split else os.path.join(app_path, 'domain', 'entities')
        entities_path = os.path.join(entities_dir, 'entities.py') if not split else os.path.join(entities_dir, entity_name.lower() + '_entity.py')

        # Crear directorios si no existen
        try:
            os.makedirs(entities_dir, exist_ok=True)
            
            # Crear archivos __init__.py
            self.__create__init__files(entities_dir)
        except OSError as e:
            self.stderr.write(self.style.ERROR(f"No se pudo crear el directorio '{entities_dir}': {e}"))
            return
        
        #si split y ya existe el archivo mostrar error
        if split and os.path.exists(entities_path):
            self.stderr.write(self.style.ERROR(f"El archivo '{entities_path}' ya existe. No se puede crear un archivo separado."))
            return

        # Escribir imports en el archivo 
        # si no existe el archivo template_imports
        if not os.path.exists(entities_path):
            #renderizar imports
            rendered_content_imports = self._renderTemplate(templateName = 'entity', fileName='imports.txt', render_params={'entity_name':entity_name})

            # Escribir imports en el archivo
            with open(entities_path, 'w') as f:
                f.write(rendered_content_imports + '\n')
            self.stdout.write(self.style.SUCCESS(f"Imports of Entity '{entity_name}' created at {entities_path}"))

        #renderizar class
        rendered_content_class = self._renderTemplate(templateName = 'entity', fileName='class.txt', render_params={'entity_name':entity_name})

        # Escribir class en el archivo
        with open(entities_path, 'a') as f:
            f.write('\n' + rendered_content_class + '\n')
        self.stdout.write(self.style.SUCCESS(f"Class of Entity '{entity_name}' created at {entities_path}"))


    def create_service(self, app_path, service_name, entity_name, class_format=False, include_crud=False, split=False, **kwargs):
        """Crea un nuevo servicio"""
        services_dir = os.path.join(app_path, 'domain') if not split else os.path.join(app_path, 'domain', 'services')
        services_path = os.path.join(services_dir, 'services.py') if not split else os.path.join(services_dir, service_name.lower() + '_service.py')

        # Crear directorios si no existen
        try:
            os.makedirs(services_dir, exist_ok=True)

            # Crear archivos __init__.py
            self.__create__init__files(services_dir)
        except OSError as e:
            self.stderr.write(self.style.ERROR(f"No se pudo crear el directorio '{services_dir}': {e}"))
            return
        
        #si split y ya existe el archivo mostrar error
        if split and os.path.exists(services_path):
            self.stderr.write(self.style.ERROR(f"El archivo '{services_path}' ya existe. No se puede crear un archivo separado."))
            return

        # Escribir imports en el archivo 
        # si no existe el archivo template_imports
        if not os.path.exists(services_path):
            #renderizar imports
            rendered_content_imports = self._renderTemplate(templateName = 'service', fileName='imports.txt', render_params={'service_name':service_name, 'entity_name':entity_name})

            # Escribir imports en el archivo
            with open(services_path, 'w') as f:
                f.write(rendered_content_imports + '\n')
            self.stdout.write(self.style.SUCCESS(f"Imports of Service '{service_name}' created at {services_path}"))

        if class_format:
            #renderizar class

            if include_crud:
                #renderizar class con crud
                rendered_content_class = self._renderTemplate(templateName = 'service', fileName='class_crud.txt', render_params={'service_name':service_name, 'entity_name':entity_name})

            else:
                #renderizar class
                rendered_content_class = self._renderTemplate(templateName = 'service', fileName='class.txt', render_params={'service_name':service_name, 'entity_name':entity_name})

        else:
            #renderizar funcion

            if include_crud:
                #renderizar funcion con crud
                rendered_content_class = self._renderTemplate(templateName = 'service', fileName='function_crud.txt', render_params={'service_name':service_name, 'entity_name':entity_name})

            else:
                #renderizar funcion
                rendered_content_class = self._renderTemplate(templateName = 'service', fileName='function.txt', render_params={'service_name':service_name, 'entity_name':entity_name})        

        # Escribir class en el archivo
        with open(services_path, 'a') as f:
            f.write('\n' + rendered_content_class + '\n')
        self.stdout.write(self.style.SUCCESS(f"Class of Service '{service_name}' created at {services_path}"))


    def create_repository(self, app_path, entity_name, include_crud, **kwargs):
        """Crea un nuevo repositorio"""
        repository_dir = os.path.join(app_path, 'infrastructure')
        repository_path = os.path.join(repository_dir, entity_name.lower() + '_repository.py')

        app_name = app_path.replace('/', '.').replace('\\', '.').replace('..', '.')

        # Crear directorios si no existen
        try:
            os.makedirs(repository_dir, exist_ok=True)

            # Crear archivos __init__.py
            self.__create__init__files(repository_dir)
        except OSError as e:
            self.stderr.write(self.style.ERROR(f"No se pudo crear el directorio '{repository_dir}': {e}"))
            return    
        
        #si ya existe el archivo mostrar error
        if os.path.exists(repository_path):
            self.stderr.write(self.style.ERROR(f"El archivo '{repository_path}' ya existe."))
            return
        
        #renderizar class
        rendered_content_class = self._renderTemplate(templateName = 'repository', fileName='class.txt', render_params={'entity_name':entity_name, 'include_crud':include_crud, 'app_name':app_name})

        # Escribir class en el archivo
        with open(repository_path, 'w') as f:
            f.write('\n' + rendered_content_class + '\n')
        self.stdout.write(self.style.SUCCESS(f"Class Repository of Entity '{entity_name}' created at {repository_path}"))


    def create_dto(self, app_path, dto_name, split=False, **kwargs):
        """Crea un nuevo DTO"""
        dtos_dir = os.path.join(app_path, 'domain') if not split else os.path.join(app_path, 'domain', 'dtos')
        dtos_path = os.path.join(dtos_dir, 'dtos.py') if not split else os.path.join(dtos_dir, dto_name.lower() + '_dto.py')

        # Crear directorios si no existen
        try:
            os.makedirs(dtos_dir, exist_ok=True)

            # Crear archivos __init__.py
            self.__create__init__files(dtos_dir)
        except OSError as e:
            self.stderr.write(self.style.ERROR(f"No se pudo crear el directorio '{dtos_dir}': {e}"))
            return
        
        #si split y ya existe el archivo mostrar error
        if split and os.path.exists(dtos_path):
            self.stderr.write(self.style.ERROR(f"El archivo '{dtos_path}' ya existe. No se puede crear un archivo separado."))
            return

        # Escribir imports en el archivo 
        # si no existe el archivo template_imports
        if not os.path.exists(dtos_path):
            #renderizar imports
            rendered_content_imports = self._renderTemplate(templateName = 'dto', fileName='imports.txt', render_params={'dto_name':dto_name})

            # Escribir imports en el archivo
            with open(dtos_path, 'w') as f:
                f.write(rendered_content_imports + '\n')
            self.stdout.write(self.style.SUCCESS(f"Imports of Dto '{dto_name}' created at {dtos_path}"))

        #renderizar class
        rendered_content_class = self._renderTemplate(templateName = 'dto', fileName='class.txt', render_params={'dto_name':dto_name})

        # Escribir class en el archivo
        with open(dtos_path, 'a') as f:
            f.write('\n' + rendered_content_class + '\n')
        self.stdout.write(self.style.SUCCESS(f"Class of Dto '{dto_name}' created at {dtos_path}"))


    def create_view_api_apiview(self, app_path, entity_name, **kwargs):
        """Crea una view para api basada en ApiView"""
        views_dir = app_path
        views_path = os.path.join(views_dir, entity_name.lower() + '_views.py')

        # Crear directorios si no existen
        try:
            os.makedirs(views_dir, exist_ok=True)

            # Crear archivos __init__.py
            self.__create__init__files(views_dir)
        except OSError as e:
            self.stderr.write(self.style.ERROR(f"No se pudo crear el directorio '{views_dir}': {e}"))
            return    
        
        #si ya existe el archivo mostrar error
        if os.path.exists(views_path):
            self.stderr.write(self.style.ERROR(f"El archivo '{views_path}' ya existe."))
            return
        
        #convertir app_path (ej: apps/ap1) a app_name (ej: apps.app1)
        app_name = app_path.replace('/', '.').replace('\\', '.').replace('..', '.')

        #renderizar view
        rendered_content_class = self._renderTemplate(templateName = 'api', fileName='apiview_views.txt', render_params={'app_name':app_name, 'entity_name':entity_name})

        # Escribir class en el archivo
        with open(views_path, 'w') as f:
            f.write('\n' + rendered_content_class + '\n')
        self.stdout.write(self.style.SUCCESS(f"Class View ApiView of Entity '{entity_name}' created at {views_path}"))


    def create_view_api_viewset(self, app_path, entity_name, **kwargs):
        """Crea una view para api basada en ApiViewSet"""
        views_dir = app_path
        views_path = os.path.join(views_dir, entity_name.lower() + '_views.py')

        # Crear directorios si no existen
        try:
            os.makedirs(views_dir, exist_ok=True)

            # Crear archivos __init__.py
            self.__create__init__files(views_dir)
        except OSError as e:
            self.stderr.write(self.style.ERROR(f"No se pudo crear el directorio '{views_dir}': {e}"))
            return    
        
        #si ya existe el archivo mostrar error
        if os.path.exists(views_path):
            self.stderr.write(self.style.ERROR(f"El archivo '{views_path}' ya existe."))
            return
        
        #convertir app_path (ej: apps/ap1) a app_name (ej: apps.app1)
        app_name = app_path.replace('/', '.').replace('\\', '.').replace('..', '.')

        #renderizar view
        rendered_content_class = self._renderTemplate(templateName = 'api', fileName='viewset_views.txt', render_params={'app_name':app_name, 'entity_name':entity_name})

        # Escribir class en el archivo
        with open(views_path, 'w') as f:
            f.write('\n' + rendered_content_class + '\n')
        self.stdout.write(self.style.SUCCESS(f"Class View ApiViewSet of Entity '{entity_name}' created at {views_path}"))


    def create_view(self, app_path, entity_name, **kwargs):
        """Crea una view para web"""
        views_dir = app_path
        views_path = os.path.join(views_dir, entity_name.lower() + '_views.py')
        forms_path = os.path.join(views_dir, entity_name.lower() + '_forms.py')

        # Crear directorios si no existen
        try:
            os.makedirs(views_dir, exist_ok=True)

            # Crear archivos __init__.py
            self.__create__init__files(views_dir)
        except OSError as e:
            self.stderr.write(self.style.ERROR(f"No se pudo crear el directorio '{views_dir}': {e}"))
            return    
        
        #si ya existe el archivo view mostrar error
        if os.path.exists(views_path):
            self.stderr.write(self.style.ERROR(f"El archivo '{views_path}' ya existe."))
            return
        
        #si ya existe el archivo form mostrar error
        if os.path.exists(forms_path):
            self.stderr.write(self.style.ERROR(f"El archivo '{forms_path}' ya existe."))
            return
        
        #convertir app_path (ej: apps/ap1) a app_name (ej: apps.app1)
        app_name = app_path.replace('/', '.').replace('\\', '.').replace('..', '.')

        #renderizar views
        rendered_content_class = self._renderTemplate(templateName = 'view', fileName='web_views.txt', render_params={'app_name':app_name, 'entity_name':entity_name})

        # Escribir views en el archivo
        with open(views_path, 'w') as f:
            f.write('\n' + rendered_content_class + '\n')
        self.stdout.write(self.style.SUCCESS(f"Class View of Entity '{entity_name}' created at {views_path}"))

        #renderizar forms
        rendered_content_forms = self._renderTemplate(templateName = 'view', fileName='web_forms.txt', render_params={'entity_name':entity_name})

        # Escribir forms en el archivo
        with open(forms_path, 'w') as f:
            f.write('\n' + rendered_content_forms + '\n')
        self.stdout.write(self.style.SUCCESS(f"Class Form of Entity '{entity_name}' created at {forms_path}"))
