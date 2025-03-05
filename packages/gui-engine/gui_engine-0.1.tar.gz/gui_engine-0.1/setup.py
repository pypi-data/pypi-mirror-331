from setuptools import setup, find_packages

setup(
    name="gui_engine",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "Pillow",
        "customtkinter",
        "WMI",
        "window-functions",
    ],
    author="rixhlivin",
    author_email="rixhlivin@gmail.com",
    description="A package for advanced GUI made with tkinter",
)