import sys
from woodcut.project import Project
from optparse import OptionParser

import pkg_resources
version = pkg_resources.require("woodcut")[0].version

def main():
    usage = "usage: %prog [options] command src_path build_path"
    parser = OptionParser(usage=usage, version="%prog {0}".format(version))
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False, help="Show more logging information")
    parser.add_option("-c", "--copy", action="store_true", dest="copy", default=False, help="Copy non-template files instead of symlinking them")
    (options, args) = parser.parse_args()
    
    if len(args) == 3 and args[0] == 'build':
        Project(src_root=args[1], build_root=args[2], copy=options.copy).build()
    elif len(args) == 3 and args[0] == 'clean':
        Project(src_root=args[1], build_root=args[2], copy=options.copy).clean()
    else:
        parser.print_usage()
    
    return 0