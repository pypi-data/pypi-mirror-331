from setuptools import setup, find_packages

setup(
    name="vaishnavi_in_states",
    version="0.1",
    packages=find_packages(),
    include_package_data=True,
    install_requires=["django"],
    license="MIT",
    description="A Django app that provides Indian state choices as a model and form field.",
    author="vaishnavi kamble",
    author_email="vaishnavikamble0106@gmail.com",
    classifiers=[
        "Framework :: Django",
        "Programming Language :: Python :: 3",
    ],
)
