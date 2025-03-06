from setuptools import setup, find_packages
setup(
    name="lpar_activation_work",
    version="1.0.0",
    packages=find_packages(),
    install_requires=["gitdb==4.0.12",
                      "GitPython==3.1.44",
                      "pytest==8.3.4",
                      "paramiko==3.5.1",
                      "requests==2.32.3",
                      "setuptools==75.8.0",
                      "zhmccli==1.12.0",
                      "twine==6.1.0",
                      "build==1.2.2",
                      "pipreqs==0.4.13",
                      ],
    entry_points={
        'console_scripts': [
            'entry_point = lpar_activation.__main__:main',]
    }
)
