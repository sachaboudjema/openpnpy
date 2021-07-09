import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="openpnpy",
    version="0.0.1",
    install_requires=[
        'flask',
    ],
    author="Sacha Boudjema",
    author_email="sachaboudjema@gmail.com",
    description="Cisco Network PnP Server",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sachaboudjema/openpnpy",
    project_urls={
        "Issues": "https://github.com/sachaboudjema/openpnpy/issues",
        "Documentation": "https://openpnpy.readthedocs.io",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "."},
    packages=setuptools.find_packages(where="."),
    python_requires=">=3.6",
)