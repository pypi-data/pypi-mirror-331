from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="simple-chat-structure",
    version="0.1.0",
    author="Vladislav K",
    author_email="vkolebcev@yandex.ru",
    description="Библиотека для управления структурой чатов и сообщений",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/VKolebcev/simple_chat_structure",
    project_urls={
        "Bug Tracker": "https://github.com/VKolebcev/simple_chat_structure/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries",
        "Topic :: Communications :: Chat",
    ],
    packages=find_packages(),
    python_requires=">=3.8",
)
