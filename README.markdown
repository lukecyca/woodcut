# Woodcut #
*Minimalist content management system for static websites*

Woodcut is a system for building static websites from Mako source files.  It will walk your source directory, process any templates it finds, and produce a complete website in the build directory, ready to `rsync` to your webserver.

Any file that ends in `.mako` is considered a template, and will be rendered as a corresponding file in the build directory (but will drop the `.mako` extension).

The entire directory structure of the source directory is replicated in the build directory, and all files not meeting the above criteria appear in the build directory as symlinks to their source files.

## Installation ##

    mbp:woodcut luke$ sudo python setup.py install

## Usage ##
You can try it on the example source tree.

    mbp:woodcut luke$ cd example/
    mbp:example luke$ woodcut build src/ build/
    Rendering htaccess.conf
    Rendering index.html
    Rendering foo.html

You will find the files rendered in the `build` directory.

## Examples ##
* <http://lukecyca.com>
* <http://bkpr.ca>
* <http://freegeekvancouver.org>
* <http://sidneyyork.com>

## Version History ##

### 0.3 ###

* Changed from Genshi to Mako templates
* Moved mako modules into build directory, and build products into <build>/root
* Removed BeautifulSoup-style template inspection

### 0.2 ###
* Generalized for other websites
* Removed all article support.  Articles can still be implemented within template code.

### 0.1 ###
* Release specific to http://lukecyca.com

