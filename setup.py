from setuptools import setup, find_packages

setup(
    name='image_gallery',
    version='1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Flask',
        'flask-cors',
        'psycopg2-binary'
    ],
    entry_points={
        'console_scripts': [
            'runserver=app:main',
        ],
    },
)


# Este arquivo define as dependências e permite instalar todas as bibliotecas necessárias com um comando.