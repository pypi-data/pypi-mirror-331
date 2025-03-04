from setuptools import setup, find_packages

setup(
    name="code2uml",
    version="0.2.5.1",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'code2uml=code2uml.code2uml:main',
        ],
    },
    install_requires=[
        'antlr4-python3-runtime'
    ],
    description='Generate UML diagrams from source code',
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    include_package_data=True,
    author='min',
    author_email='testmin@outlook.com',
    url='https://github.com/passion-coder-min/code2uml.git',
    project_urls = {
      "Bug Tracker": "https://github.com/passion-coder-min/code2uml/issues",
      "Documentation": "https://github.com/passion-coder-min/code2uml/README.md",
      "Source Code": "https://github.com/passion-coder-min/code2uml.git", 
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Code Generators',
    ],
)
