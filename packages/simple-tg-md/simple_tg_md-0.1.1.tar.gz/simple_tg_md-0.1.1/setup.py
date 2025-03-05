from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="simple-tg-md",
    version="0.1.1",
    author="HalPerson",
    author_email="vkolebcev@yandex.ru",
    description="Библиотека для конвертирования текста в Telegram Markdown V2",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/VKolebcev/simple-tg-md",
    project_urls={
        "Bug Tracker": "https://github.com/VKolebcev/simple-tg-md/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    packages=find_packages(),
    python_requires=">=3.9",
    keywords='telegram markdown conversion',
)
