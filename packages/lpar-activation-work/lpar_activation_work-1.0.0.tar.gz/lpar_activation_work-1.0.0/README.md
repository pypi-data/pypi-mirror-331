Description:
*************
Python code to take lpar, ipaddress, script directory and
script command as the input .
First step is call the zhmclient to activate the lpar(@srivaishnavi
is working on correct way to activate the lpar) .
Sleep for 10 minutes
ssh to the ipaddress (Linux guest ip address)
cd to the dir(/ffdc/u/eATS_automation) on the ssh session
invoke the script command (sh makeloop.sh) on the ssh session ,
collect the output printed on the ssh session and print it

config.json file structure:
****************************
{
    "host_name": "9.56.198.101",
    "hmcm_user_name": "root",
    "hmcm_pwd": "passw0rd",
    "cpc": "A02",
    "lpar": "LINUX1B",
    "system_host": "9.56.198.161",
    "userid": "c-kuca897@nomail.relay.ibm.com",
    "user_pwd": "BV1#l2rTk*0jGN$33",
    "ssh_key_path": "SSH_KEY_PATH",
    "script_details": {
        "token": "bb11f4a7812ec380752863f9b220ad562912bd80",
        "name": "FhaAggr.sh",
        "url": "https://raw.github.ibm.com/systemz/testcase_catalog/main/eats/scripts/",
        "exec_path": "/ffdc/u/eATS_automation/",
        "local_path": "./"
    }
}

How to run the script:
**********************

python __main__.py config.json

How to create python package/librabry:
***************************************

Creating a Python package can be a rewarding experience, and it's a great way to share your code with others. Here are the steps to create a Python package:

1. Set Up Your Project Structure

Organize your project directory with the following structure:

my_package/
├── my_package/
│   ├── __init__.py
│   ├── module1.py
│   └── module2.py
├── tests/
│   ├── __init__.py
│   └── test_module1.py
├── README.md
├── setup.py
└── requirements.txt

2. Write Your Code

Place your Python code in the my_package directory. Each .py file represents a module in your package. The __init__.py file can be used to initialize the package and define what is available when the package is imported.

3. Create a setup.py File

This file contains metadata about your package and instructions on how to install it. Here’s a basic example:

from setuptools import setup, find_packages

setup(
    name='my_package',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        # List your package dependencies here
    ],
    author='Your Name',
    author_email='your.email@example.com',
    description='A brief description of your package',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/my_package',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)

4. Add a README.md File

This file provides an overview of your package, how to install it, and how to use it. Markdown format is commonly used for this file.

5. Specify Dependencies

List any external packages your package depends on in the requirements.txt file. This helps users install all necessary dependencies easily.

6. Write Tests

Create tests for your package in the tests directory. Using a testing framework like unittest or pytest is recommended. Here’s a simple example using unittest:

import unittest
from my_package import module1

class TestModule1(unittest.TestCase):
    def test_function(self):
        self.assertEqual(module1.some_function(), expected_result)

if __name__ == '__main__':
    unittest.main()

7. Build Your Package

Use the following command to build your package:

python setup.py sdist bdist_wheel


This will create distribution archives in the dist directory.

8. Upload to PyPI

To share your package with the Python community, you can upload it to the Python Package Index (PyPI). First, install twine:

pip install twine


Then, upload your package:

twine upload dist/*

9. Install and Test Your Package

Finally, install your package locally to ensure everything works as expected:

pip install .


By following these steps, you'll have a Python package that is well-structured, documented, and ready to be shared with others. Happy coding!