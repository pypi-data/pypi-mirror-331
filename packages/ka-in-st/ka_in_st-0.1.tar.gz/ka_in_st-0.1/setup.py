from setuptools import setup, find_packages

setup(
    name="ka_in_st",
    version="0.1",
    packages=find_packages(),
    include_package_data=True,
    install_requires=["django"],
    license="MIT",
    description="A Django app that provides Indian state choices as a model and form field.",
    author="Kamal Sir",
    author_email="kamalsir@ymail.com",
    classifiers=[
        "Framework :: Django",
        "Programming Language :: Python :: 3",
    ],
)
