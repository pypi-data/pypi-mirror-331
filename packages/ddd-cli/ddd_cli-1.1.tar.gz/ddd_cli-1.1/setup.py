from setuptools import setup, find_packages

setup(
    name='ddd_cli',
    version='1.1',
    description='CLI para agregar soporte DDD a proyectos Django',
    author='Ragnar Bermúdez La O',
    author_email='ragnarbermudezlao@gmail.com',
    packages=find_packages(),
    install_requires=['django', 'jinja2'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Framework :: Django',
    ],
    entry_points={
        'console_scripts': [
            'manage.py = django.core.management:execute_from_command_line',
        ],
    },
)
