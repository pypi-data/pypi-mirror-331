from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="HelpMLA",
    version="0.1",
    author="Ваше Имя",
    author_email="ваш.email@example.com",
    description="Библиотека с четырьмя методами, возвращающими 1, 2, 3 и 4.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ваш_репозиторий/HelpDSF",  # Ссылка на репозиторий
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
