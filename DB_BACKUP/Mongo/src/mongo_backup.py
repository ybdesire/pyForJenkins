#! /usr/bin/env python
# -*- coding: utf-8 -*-

'''MongoDB logic backup tool
'''
import sys
import logging
import argparse

__application__ = 'MongoDB logic backup tool'
__version__ = '1.0'

LOG = None


def main(argv):
    cmd_parser = argparse.ArgumentParser();
    cmd_parser.add_argument('-v', '--version', action='version', version='{0}'.format(__version__))
    cmd_parser.add_argument('host', help='mongo db server host/ip')
    cmd_parser.add_argument('port', help='mongo db server port')
    cmd_parser.add_argument('out', help='output file name with path')
    cmd_parser.add_argument('-u', '--userName', help='mongo db user name')
    cmd_parser.add_argument('-p', '--password', help='mongo db password')
    cmd_parser.add_argument('-t', '-backupTime', help='every day backup time. Multiple time can be divided by ","')
    cmd_parser.add_argument('-d', '-db', help='db names to be backupped. Multiple db can be divided by ","')
    cmd_parser.add_argument('-m', '--mode', help='running mode: test/release')
    args = cmd_parser.parse_args(argv[1:])
    print(args)
if __name__ == '__main__':
    main(sys.argv)
    
