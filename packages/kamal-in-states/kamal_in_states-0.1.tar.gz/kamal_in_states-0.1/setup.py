from setuptools import setup, find_packages

setup(
    name='kamal_in_states',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'django',
        'djangorestframework',
    ],
    include_package_data=True,
    description="A Django REST API providing a list of all Indian states",
    author="Kamal Sir",
    author_email="kamalsir@ymail.com",
    url="https://github.com/yourusername/django-indian-states",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Framework :: Django",
        "License :: OSI Approved :: MIT License",
    ],
)
