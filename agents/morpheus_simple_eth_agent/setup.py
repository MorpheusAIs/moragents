from setuptools import setup, find_packages

# Read the contents of your requirements.txt file
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='simple_eth_agent',
    version='0.0.0',
    author='Morpheus',
    author_email='',
    description='AI chatbot for web3 wallet integration',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',  # This is important for README.md files
    url='https://github.com/MorpheusAIs/Morpheus',
    packages=find_packages(exclude=('tests', 'docs')),
    install_requires=requirements,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    python_requires='>=3.7',
    entry_points={
        'console_scripts': [
            'example-command=example_package.module:main_function',
            # This allows the user to run a specific function as a command line tool
        ],
    },
    include_package_data=True,
    package_data={
        # If any package contains *.txt or *.rst files, include them:
        '': ['*.txt', '*.rst', '*.md'],
        # And include any *.msg files found in the 'example_package' package, too:
        'example_package': ['*.msg'],
    },
    keywords='morpheus ai web3',
    license='MIT',
)
