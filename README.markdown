# Woodcut #
*Minimalist content management system for static websites*

Woodcut is a system for building static websites from Genshi source files.  It will walk your source directory, process any templates it finds, and produce a complete website in the build directory, ready to `rsync` to your webserver.

Templates are processed as follows:

* `foo.xhtml` is validated and processed as XHTML with Genshi and XInclude, producing `foo.html` in the build directory.
* `foo.bar.xml` is validated and processed as XML, producing `foo.bar` in the build directory.
* `foo.bar.newtxt` is processed as a Genshi NewTextTemplate, and produces `foo.bar` in the build directory.

The entire directory structure of the source directory is replicated in the build directory, and all files not meeting the above criteria appear in the build directory as symlinks to their source files.

## Installation ##
Download and install [BeautifulSoup](http://www.crummy.com/software/BeautifulSoup/) and [Genshi](http://genshi.edgewall.org/wiki/Download)

Install Woodcut:

    mbp:woodcut luke$ sudo python setup.py install

## Usage ##
You can try it on the example source tree.

    mbp:woodcut luke$ cd example/
    mbp:example luke$ woodcut --build src/ build/
    Rendering htaccess.conf
    Rendering index.html
    Rendering foo.html

## Examples ##
A live example is <http://lukecyca.com>.
