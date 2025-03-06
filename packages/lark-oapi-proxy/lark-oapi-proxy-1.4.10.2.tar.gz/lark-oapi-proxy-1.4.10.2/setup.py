from distutils.core import setup

from setuptools import find_packages

from lark_oapi.core.const import VERSION, UTF_8

with open("README.md", mode="r", encoding=UTF_8) as f:
    readme = f.read()

setup(
    name="lark-oapi-proxy",
    version=VERSION + ".2",
    description="Lark OpenAPI SDK for Python with Proxy Support",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="yesgit", 
    author_email="yestion@gmail.com",
    url="https://github.com/yesgit/oapi-sdk-python",
    packages=find_packages(),
    install_requires=[
        "requests",
        "requests_toolbelt",
        "pycryptodome",
        "websockets",
        "httpx",
        "websockets-proxy"
    ],
    extras_require={
        "flask": ["Flask>=2"]
    },
    python_requires=">=3.7",
    keywords=["Lark", "OpenAPI", "Proxy"],
    include_package_data=True,
    project_urls={
        "Source": "https://github.com/yesgit/oapi-sdk-python",
    },
)
