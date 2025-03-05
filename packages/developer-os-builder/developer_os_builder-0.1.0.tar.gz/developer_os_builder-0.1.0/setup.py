from setuptools import setup, find_packages

setup(
    name="developer-os-builder",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[],
    entry_points={
        "console_scripts": [
            "start-vmware=developer.vm:start_vmware",
            "start-virtualbox=developer.vm:start_virtualbox",
            "create-iso=developer.iso:create_iso",
        ],
    },
    author="Твое Имя",
    author_email="твоя@почта.com",
    description="Пакет для разработки ОС, запуска виртуальных машин и сборки ISO",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/твой-профиль/developer",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
    ],
    python_requires=">=3.6",
)
