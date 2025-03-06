from setuptools import setup, find_packages

setup(
    name='CoffeeAI',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'flask',
        'numpy',
    ],
    author='OUBStudios',
    author_email='oubdocs.main@example.com',
    description='A neural network library for CoffeeAI.',
    url='https://github.com/yourusername/coffeeai',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
