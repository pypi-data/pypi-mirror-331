# DDD CLI

Este paquete agrega comandos personalizados a Django para facilitar la implementación de una arquitectura Domain-Driven Design (DDD).

## Comandos disponibles

- `python manage.py ddd create-entity <app_path> <entity_name> [--split]`
- `python manage.py ddd create-service <app_path> <entity_name> <service_name> [--class-format] [--include-crud] [--split]`
- `python manage.py ddd create-repository <app_path> <entity_name> [--include-crud]`
- `python manage.py ddd create-dto <app_path> <dto_name> [--split]`
- `python manage.py ddd create-view-api-apiview <app_path> <entity_name>`
- `python manage.py ddd create-view-api-viewset <app_path> <entity_name>`
- `python manage.py ddd create-view <app_path> <entity_name>`

## Instalación
pip install .

## Reinstalacion o instalacion en modo debug
pip install -e .