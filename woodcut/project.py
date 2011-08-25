#!/usr/bin/python

import os
import os.path
from datetime import datetime
from mako.template import Template
from mako.lookup import TemplateLookup
from mako.exceptions import text_error_template, SyntaxException, CompileException


IGNORE_FILES = ['.DS_Store']
IGNORE_DIRECTORIES = ['templates']

class Project(object):
    def __init__(self, src_root='', build_root=''):
        self.src_root = os.path.abspath(src_root)
        self.build_root = os.path.abspath(build_root)
        self.lookup = TemplateLookup(directories=[self.src_root],
                                     module_directory=os.path.join(self.build_root, 'modules'),
                                     output_encoding='utf-8',
                                     input_encoding='utf-8',
                                     )
        
    
    def build_file(self, root_relative_src_path):
        def relative_path(path):
            """Translates a root-relative path to a path relative to this file"""
            backout_path = os.path.relpath('.', os.path.dirname(root_relative_src_path))
            return os.path.normpath(os.path.join(backout_path, path))
        
        # Absolute paths to source and build objects
        src_path = os.path.normpath(os.path.join(self.src_root, root_relative_src_path))
        build_path = os.path.normpath(os.path.join(self.build_root, 'root', root_relative_src_path))
        
        if os.path.exists(build_path):
            os.unlink(build_path)
        
        extension = os.path.splitext(src_path)[1]
        
        # Skip non-templates, and just link them to the source file
        if extension not in ['.mako']:
            os.symlink(src_path, build_path)
            return
        
        # Determine output filename
        build_path = os.path.splitext(build_path)[0]
        
        # Render the template to the output path
        print "Rendering %s" % build_path

        mako_src = self.lookup.get_template(root_relative_src_path)

        fh = open(build_path, 'w')
        fh.write(mako_src.render(relative_path=relative_path))
        fh.close()

    def build(self):
        if not os.path.exists(self.build_root):
            os.mkdir(self.build_root)
        if not os.path.exists(os.path.join(self.build_root, 'root')):
            os.mkdir(os.path.join(self.build_root, 'root'))
        os.chdir(self.src_root)
        for path, dirs, files in os.walk('.'):
            for d in dirs:
                if d in IGNORE_DIRECTORIES:
                    dirs.remove(d)
                elif not os.path.exists(os.path.join(self.build_root, 'root', path, d)):
                    os.mkdir(os.path.join(self.build_root, 'root', path, d))
            for f in [x for x in files if x not in IGNORE_FILES]:
                #try:
                    self.build_file(os.path.join(path, f))
                #except Exception, e:
                #    print '  ERROR: ' + str(e)

    def clean(self):
        """Delete everything in the build directory"""
        for root, dirs, files in os.walk(self.build_root, topdown=False):
            for f in files:
                os.remove(os.path.join(root,f))
            for d in dirs:
                os.rmdir(os.path.join(root,d))
                