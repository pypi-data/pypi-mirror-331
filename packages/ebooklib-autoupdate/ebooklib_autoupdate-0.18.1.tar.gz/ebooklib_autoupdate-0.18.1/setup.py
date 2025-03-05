import io
import re

from setuptools import setup


def read(path):
    with io.open(path, mode="r", encoding="utf-8") as fd:
        content = fd.read()
    # Convert Markdown links to reStructuredText links
    return re.sub(r"\[([^]]+)\]\(([^)]+)\)", r"`\1 <\2>`_", content)


setup(
    name="EbookLib",
    version="0.18.1",
    author="Aleksandar Erkalovic",
    author_email="aerkalov@gmail.com",
    packages=["ebooklib", "ebooklib.plugins"],
    url="https://github.com/aerkalov/ebooklib",
    license="GNU Affero General Public License",
    description="Ebook library which can handle EPUB2/EPUB3 format",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    keywords=["ebook", "epub"],
    classifiers=[
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    install_requires=["lxml", "six"],
)
