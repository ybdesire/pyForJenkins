#! /usr/bin/env python
# -*- coding: utf-8 -*-

'''static code analyzer for detecting hardcode strings
'''

# python3 compatible support
from __future__ import print_function
from __future__ import unicode_literals
try:
    unicode
except NameError:
    unicode = str

import sys
import os
import exceptions
import csv
import argparse
import logging
import types
import glob
import imp
import codecs
import io
import contextlib
import itertools
import functools
from datetime import datetime, time
import platform
from collections import defaultdict
from pyparsing import *

# use regex instead of re to overcome the max 100 groups limitation
# import re
import regex as re

try:
    import html.parser # python3
    html_unescape = html.parser.HTMLParser().unescape
except:
    import HTMLParser
    html_unescape = HTMLParser.HTMLParser().unescape

__author__ = 'xxxx'
__email__ = 'xxxxxxxx'
__version_info__ = (1, 32, 0)
__version__ = '.'.join(str(i) for i in __version_info__)
__tool__ = 'x'

    
SEVERITY_ERROR = 'error'
SEVERITY_WARNING = 'warning'



def main(argv):
    logging.basicConfig(stream=sys.stdout, level=logging.WARNING, format="%(message)s")
    
    root, basename, ext = get_self_path_info(argv[0])
    usage = '''
   %prog <{base}.config path>
or %prog <directory>
it will read *{base}.config in the directory.
If no input file the current working directory is assumed
see http://citrixwiki/String_detector for more information
'''.format(base=basename)
    
    cmd_parser = argparse.ArgumentParser()

    cmd_parser.add_argument('-v', '--version', action='version', version='%(prog)s {}'.format(__version__))
    
    cmd_parser.add_argument('-c', '--find-content', metavar='.*?hello.*',
                          help='grep hardcode string whose content matched the given regular expression')
    
    cmd_parser.add_argument('-t', '--tab-width', metavar='4', type=int,
                          help='specify tab width if editor requires vision column position instead of physical position')
    
    cmd_parser.add_argument('-i', '--initialize', action="store_true",
                          help='initialize a directory by generating a default string_detector.config file')
    
    cmd_parser.add_argument('-d', '--details', metavar="string_detector_result_details.csv",
                          help='output string detector result details into CSV file')
    
    cmd_parser.add_argument('-s', '--summary', metavar="string_detector_result_summary.csv",
                          help='output string detector result summary into CSV file')
    
    cmd_parser.add_argument('-l', '--log-level', metavar="error", default="warning", type=logLevel,
                            help='set output level, only "critical", "error", "warning", "info", "debug" are valid')
    
    cmd_parser.add_argument('-r', '--relative-path', action="store_true", default=False,
                            help='output in relative path instead of full path')
    
    cmd_parser.add_argument('path', help="config file path or target root directory for detection", nargs='?', default='.')
    
    args = cmd_parser.parse_args(argv[1:])
    
    logging.getLogger().setLevel(args.log_level)
        
    path = os.path.abspath(args.path)
    if os.path.isdir(path):
        paths = glob.glob(os.path.join(path, '*' + basename + '.config'))
        paths.append(os.path.join(path, basename+'.config'))
        path = os.path.abspath(paths[0])
    
    HERE = os.path.dirname(path)

    report = Report(basename+ext, __version__)
    logging.critical(safe_string(report.title()))
    
    if args.initialize:
        if os.path.exists(path):
            logging.critical(safe_string('could not generate string_detector.config, {} already exists!\n'.format(path)))
        else:
            try:
                with open(path, 'w') as f:
                    f.write(DEFAULT_CONFIG.replace('{version}', __version__).replace('{now}', datetime.now().isoformat()))
                    logging.critical(safe_string('config file <{}> genereted.\n'.format(path)))
            except Exception as e:
                os.remove(path)
                sys.exit(0)
                
    try:
        config = get_config(path)
        if not config:
            logging.critical(safe_string('using build-in config (it could be output to "string_detector.config" for further customization using "-i" option)\n'.format(path)))
            config = get_config_from_string(DEFAULT_CONFIG)
        
        ignore_file = [re.compile(i) for i in config('IGNORE_FILE_PATTERN', [])]
        ignore_string_in_content = [compile_re_for_whole(i) for i in config('IGNORE_STRING_IN_CONTENT_PATTERN', [])]
        ignore_string_in_function = [(compile_re_for_whole(name), pos) for name, pos in config('IGNORE_STRING_IN_FUNCTION_PATTERN', [])]
        ignore_string_in_line = [tuple(compile_re_for_whole(i) for i in j) for j in config('IGNORE_STRING_IN_LINE_PATTERN', [])]
        if args.find_content:
            args.find_content = compile_re_for_whole(args.find_content)
        
        xpath_attribute_pairs = config('XPATH_ATTRIBUTE', {})
        for xpath, attributes in xpath_attribute_pairs.iteritems():        
            for attribute, ignore_xml_contents in attributes.iteritems():
                attributes[attribute] = [compile_re_for_whole(i) for i in ignore_xml_contents]
                
        DIAGNOSTICS_FORMAT = normalize_format(config(
            'DIAGNOSTICS_FORMAT',
            DEFAULT_DIAGNOSTICS_FORMATS[0]))

        if args.relative_path:
            DIAGNOSTICS_FORMAT = DIAGNOSTICS_FORMAT.replace('{file_path}', '{rel_file_path}')
        else:
            DIAGNOSTICS_FORMAT = DIAGNOSTICS_FORMAT.replace('{rel_file_path}', '{file_path}')
            
        hide_errors = {}

        hide_error_file = config('HIDE_ERROR_FILE', '{here}/string_detector.hide_error.txt')
        hide_error_file = normalize_format(hide_error_file).format(here=HERE)
        if os.path.isfile(hide_error_file):
            report.hide_error_file = hide_error_file
            logging.info('reading hide error file: {} ...'.format(hide_error_file))            
            hide_errors = get_hide_errors(hide_error_file, DIAGNOSTICS_FORMAT)
            logging.info('{} hide error message(s) loaded.'.format(len(hide_errors)))
        else:
            pass
            
    except Exception as e:
        error = unicode(e)        
        line = get_python_error_location(error)
        file_path = os.path.abspath(path)
        logging.critical(safe_string('{}({}): error: {}\n'.format(file_path, line, error)))
        cmd_parser.print_help()
        return -1
    
    details = None
    if args.details:
        details_file = open(args.details, 'wb')
        details = csv.writer(details_file)
        details.writerow(['file', 'line', 'severity', 'column', 'code', 'columnEnd', 'context'])
        
    extensions = config('SOURCE_EXTENSTIONS',
           ['.h', '.c', '.cpp', '.hpp', '.c++', '.cxx', # C/C++
            '.java', # Java
            '.js', # Javascript
            '.cs', # C#
            '.vb', # Visual Basic
            '.m', '.mm', # PowerShell
            '.ps1', ' .psm1', '.psd1',
            '.xml', '.xaml', # xml
            '.html', '.xhtml', '.htm',
            '.aspx', '.ascx', # ASP.NET
            '.cshtml', # ASP.NET Razor C#
            ])
    
    if isinstance(DIAGNOSTICS_FORMAT, unicode):
        DIAGNOSTICS_FORMAT = DIAGNOSTICS_FORMAT.encode('utf-8')
    
    for top in (normalize_format(i).format(here=HERE) for i in config('SOURCE_DIRECTORIES')):
        logging.info(safe_string('scanning {} ...\n'.format(os.path.abspath(top))))
        files = get_files(HERE, top, extensions, ignore_file)
        for r in get_hardcode_strings(
            files, report,
            ignore_string_in_content, ignore_string_in_function, ignore_string_in_line,
            xpath_attribute_pairs, config('IGNORE_XPATH', []),
            args.find_content, hide_errors):
            
            report.add_result(r)
            r.output_console(DIAGNOSTICS_FORMAT, args.tab_width)
            r.output_csv(details, args.tab_width)
                
    if details:
        details_file.close()
                
    logging.critical(safe_string(report.result()))

    if args.summary:
        with open(args.summary, 'wb') as summary_file:
            summary = csv.writer(summary_file)
            summary.writerow(['files', 'lines', 'errors', 'warnings', 'items', 'begin', 'end', 'name', 'version'])
            summary.writerow([report.file_count, report.line_count,
                              report.error_count, report.warning_count, report.string_count,
                              report.begin_time_utc.isoformat(), report.end_time_utc.isoformat(),
                              __tool__, __version__])
    
    return report.error_count + report.warning_count
    
if __name__ == '__main__':
    sys.exit(main(sys.argv))
