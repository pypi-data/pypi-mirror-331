from setuptools import setup, find_packages

setup(
    name="NanoJson",
    version="1.1",
    author="Mohammed Ahmed Ghanam",
    author_email="mghanam883@outlook.com",
    description='A Python library for organizing and loading bot functions from external files for the Telebot library. Simplifies bot code management by allowing the use of separate files for bot commands and functions.',
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://t.me/midoghanam",
    project_urls={
        'Channel': 'https://t.me/mido_ghanam'
    },
    packages=find_packages(),
    install_requires=[
        'pyTelegramBotAPI>=4.0.0',
        'requests'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)