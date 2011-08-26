import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "woodcut",
    version = "0.3.0",
    author = "Luke Cyca",
    author_email = "me@lukecyca.com",
    description = ("Minimalist content management system for static websites."),
    license = "BSD",
    keywords = "mako template static web development",
    url = "https://github.com/lukecyca/woodcut",
    long_description=read('README.markdown'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Topic :: Internet :: WWW/HTTP :: Site Management",
        "Topic :: Text Processing :: Markup",
    ],
    
    packages=['woodcut'],
    install_requires=["Mako>=0.4.2"],
    
    entry_points = {
        'console_scripts': [
            'woodcut = woodcut:main',
        ]
    }
)
