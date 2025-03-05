from setuptools import setup

setup(
    name='endecryption',
    version='0.0.1',
    description='Package to encrypt and decrypt data',
    # long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='Chirag Kumar',
    author_email='chiragkumarmahto@gmail.com',
    packages=['encrypt_decrypt', 'encrypt_decrypt.migrations'],
	classifiers=[
		"Intended Audience :: Developers",
		"Programming Language :: Python :: 3",
		"Topic :: Utilities"
	],
    install_requires=[
        'Django>=3.2.16',
        'simplejson>=3.17.2',
        'pycryptodome>=3.16.0',
    ],
	include_package_data=True
)