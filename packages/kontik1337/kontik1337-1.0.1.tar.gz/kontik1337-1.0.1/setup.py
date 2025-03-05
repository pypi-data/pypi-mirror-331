from setuptools import setup, find_packages

setup(
    name='kontik1337',
    version='1.0.1',
    py_modules=['kontik1337'],  # Include your module directly
    install_requires=[
        'discord.py==1.7.3',
        'requests',
        'colorama',
        'psutil',
        'pyperclip'
    ],
    
    entry_points={
        'console_scripts': [
            'kontik1337=kontik1337:main',  # Update the entry point to match your module name
        ],
    },
    author='Kontik-1337',
    author_email='kontik1337@proton.me',
    url='https://github.com/kontik_dev/',
    description='A Discord Selfbot for Clone Discord Server',
    long_description="",
    long_description_content_type='text/markdown',
    license='MIT',
    classifiers=[
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
    ],
    keywords='discord selfbot clone kontik1337',
)
