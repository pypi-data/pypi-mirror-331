from setuptools import setup, find_packages

setup(
    name="szn-search-mlops-serp-downloader",
    version="0.1.16",
    packages=find_packages(),
    description="SERP downloader and verifier",
    author="Christopher Django",
    author_email="zombei2001@gmail.com",
    url="https://serpsz.com/szn-search-mlops-serp-downloader",
    entry_points={
        "console_scripts": [
            "szn_search_mlops_serp_downloader=szn_search_mlops_serp_downloader:main",
        ],
    },
)
