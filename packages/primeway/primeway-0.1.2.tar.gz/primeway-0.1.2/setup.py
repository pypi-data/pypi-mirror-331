from setuptools import setup, find_packages

setup(
    name='primeway',
    version='0.1.2',
    description='Cli for primeway.io',  
    long_description=open('README.md').read(),  
    author='Nikita Lavrenov',  
    author_email='keith.la.00@gmail.com',
    license='MIT',  
    classifiers=[  
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    keywords='primeway, mlops',  
    packages=find_packages(),
    install_requires=[
        'click',
        'pyyaml',
        'requests',
        'tabulate',
        'sseclient-py',
        'python-dotenv',
    ],
    python_requires='>=3.10', 
    entry_points={
        'console_scripts': [
            'primeway=primeway.cli.entry:primeway_cli',
        ],
    },
    include_package_data=True,
)