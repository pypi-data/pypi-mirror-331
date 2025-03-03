from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="HelpDSFx",
    version="0.2",
    author="Ваше Имя",
    author_email="ваш.email@example.com",
    description="Библиотека для взаимодействия с DeepSeek через aitunnel.ru",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ваш_репозиторий/HelpDSFx",  # Ссылка на репозиторий
    packages=find_packages(),
    install_requires=[
        "openai",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
