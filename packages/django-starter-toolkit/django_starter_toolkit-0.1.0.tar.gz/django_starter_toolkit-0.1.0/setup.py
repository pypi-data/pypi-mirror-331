from setuptools import setup, find_packages

setup(
    name="django-starter-toolkit",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "Django>=2.2",         # Django
        "requests",            # Para peticiones HTTP
        "pandas",              # Manejo de dataframes y análisis de datos
        "beautifulsoup4",      # Para parsear HTML con BeautifulSoup
        "firebase-admin",      # Para interactuar con Firebase
        "pymongo",             # Para el módulo bson (si usas bson de pymongo)
        "django-tinymce==3.5.0",  # Para TinyMCE en Django
        "django-autocomplete-light",  # Para autocompletar campos en Django
    ],
    author="Tu Nombre",
    author_email="tu.email@example.com",
    description="Un toolkit con utilidades y helpers para Django, que incluye formularios, funciones JS y utilidades generales.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/tuusuario/django-starter-toolkit",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Framework :: Django",
        "License :: OSI Approved :: MIT License",
    ],
)
