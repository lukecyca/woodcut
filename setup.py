from setuptools import setup

setup(
    name="woodcut",
    version="0.6.0",
    author="Luke Cyca",
    author_email="me@lukecyca.com",
    description="Minimalist content management system for static websites.",
    license="MIT",
    keywords="mako template static web development",
    url="http://wiki.github.com/lukecyca/woodcut",
    long_description="Woodcut is a system for building static websites from Mako source files. It will walk your source directory, process any templates it finds, and produce a complete website in the build directory, ready to rsync to your webserver.",
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Natural Language :: English",
        "Topic :: Internet :: WWW/HTTP :: Site Management",
        "Topic :: Text Processing :: Markup",
    ],

    packages=['woodcut'],
    install_requires=["Mako>=1.2.4"],

    entry_points={
        'console_scripts': [
            'woodcut = woodcut:main',
        ]
    }
)
