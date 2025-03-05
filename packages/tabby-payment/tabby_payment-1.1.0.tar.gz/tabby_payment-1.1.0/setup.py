import setuptools


def readme():
    with open("readme.md", "r") as f:
        return f.read()


setuptools.setup(
    name="tabby-payment",
    version="1.1.0",
    author="Akinon",
    author_email="dev@akinon.com",
    description="A common library for provide payment gateway for Tabby Payment.",
    long_description=readme(),
    long_description_content_type="text/markdown",
    url="https://bitbucket.org/akinonteam/tabby-payment",
    packages=setuptools.find_packages(exclude=["tests", "tests.*", "dummy.*"]),
    zip_safe=False,
    install_requires=[
        "Django>=2.2.9,<4.0",
        "requests",
        "djangorestframework>=3.11.0,<3.15",
        "orjson==3.10.3",
        "requests-mock==1.8.0",
        "mock==4.0.3",
    ],
    package_data={"tabby_payment": ["templates/*"]},
    include_package_data=True
)
