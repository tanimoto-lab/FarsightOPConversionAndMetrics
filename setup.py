from setuptools import setup, find_packages
setup(
    name="FarsightOPConv",
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    packages=find_packages(exclude=["^\."]),
    exclude_package_data={'': ["Readme.md"]},
    install_requires=["numpy>=1.15",
                      "matplotlib>=2.2.3",
                      "pandas>=0.23",
                      "xlrd>=1.0.0",
                      "openpyxl>=2.4.5",
                      "scikit-image>=0.14"
                      ],

    python_requires=">=3.6"

)