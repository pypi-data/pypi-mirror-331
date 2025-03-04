from setuptools import setup, find_packages

setup(
    name="assignment_template_creator",
    version="1.0.3",
    packages=find_packages(),
    py_modules=["template_creator"],
    install_requires=[
        "colorama",
        "python-docx"],
    entry_points={
        "console_scripts": [
            "create_template=template_creator:main"]},
    author="stasik",
    description="the ultimate tool fpor CS assignment template generatipon.",
    classifiers=[
        "Programming Language :: Python :: 3", 
        ],
    )
