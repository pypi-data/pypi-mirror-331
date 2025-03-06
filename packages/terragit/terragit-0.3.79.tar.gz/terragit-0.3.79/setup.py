from setuptools import find_packages, setup

classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Operating System :: Microsoft :: Windows :: Windows 10",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
]



setup(
    name="terragit",
    version="0.3.79",
    description="terragit package",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://gitlab.com/commons-acp/python/terraform-gitlab",
    author="hana.mansia",
    author_email="hana.mansia@allence-tunisie.com",
    maintainer="hana.mansia",
    maintainer_email="hana.mansia@allence-tunisie.com",
    keywords=[
        "terragit",
        "terraform",
        "git",
        "automation",
        "gitlab",
        "pipeline",
        "ci/cd",
    ],
    license="MIT",
    classifiers=classifiers,
    packages=find_packages(),
    install_requires=["pandas"],
    entry_points=({"console_scripts": ["terragit = terragit.__main__:main"]}),
)
