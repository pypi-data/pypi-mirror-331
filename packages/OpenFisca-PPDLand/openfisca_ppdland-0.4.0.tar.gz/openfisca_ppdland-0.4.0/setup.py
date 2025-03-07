from setuptools import setup, find_packages

setup(
    name = "OpenFisca-PPDLand",
    version = "0.4.0",
    author = "Sylvain Duchesne",
    author_email = "sylvain.duchesne@ipp.eu",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: POSIX",
        "Programming Language :: Python",
        "Topic :: Scientific/Engineering :: Information Analysis",
        ],
    description = "OpenFisca tax and benefit system for PPDLand",
    keywords = "benefit microsimulation social tax",
    license ="http://www.fsf.org/licensing/licenses/agpl-3.0.html",
    url = "https://github.com/openfisca/country-template",
    include_package_data = True,  # Will read MANIFEST.in
    install_requires = [
        "OpenFisca-Core >= 43, < 44",
        "OpenFisca-Survey-Manager >= 3, < 4.0",
        "matplotlib",
        "scipy",
        ],
    packages = find_packages(exclude=["openfisca_france.tests*"]),
    )
