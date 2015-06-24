#! /usr/bin/env python
# -*- coding: utf-8 -*-

'''mysql db backup tool(python 3.4.3)
'''

import logging
import sys
import argparse
import time
import subprocess
from datetime import datetime

__application__ = 'mysql logic backup tool'
__version__ = '1.0'

LOG = None
MYSQL_BACKUP_CMD = 'mysqldump -P{port} -u{user} -p{password} {database} > {output}'

def log_initialize(arguments):
    global LOG
    try:
        LOG = logging.getLogger(__name__)
        LOG.setLevel(logging.INFO)
        formatter = logging.Formatter("[%(levelname)s]: %(message)s")
        if arguments.log:
            file_handler = logging.FileHandler(filename = arguments.log, mode = 'w', encoding = "utf_8_sig", delay = False)
            file_handler.setFormatter(formatter)
            LOG.addHandler(file_handler)
        stream_handler = logging.StreamHandler(stream = sys.stdout)
        stream_handler.setFormatter(formatter)
        LOG.addHandler(stream_handler)
    except Exception as e:
        print("[CRITICAL]: An error occurred when initializing logging: {exception}".format(exception = e))

def quit_application(status):  
    if(status==-1):
        LOG.info("{application} exited abnormally".format(application=__application__))
    else:
        LOG.info("{application} exited normally".format(application=__application__))
    sys.exit(status)

def process_cmd(cmd, mode):
    if (mode=='test'):
        LOG.info(''.join(['TEST_CMD ', cmd]))
        quit_application(0)
    else:
        subprocess.Popen(cmd, shell=True)

def main(argv):
    cmd_parser = argparse.ArgumentParser();
    cmd_parser.add_argument('-v', '--version', action='version', version='{0}'.format(__version__))
    cmd_parser.add_argument('port', help='mysql server port')
    cmd_parser.add_argument('host', help='mysql server host/ip')
    cmd_parser.add_argument('user', help='mysql user name')
    cmd_parser.add_argument('password', help='mysql password')
    cmd_parser.add_argument('db', help='db names to be backupped. Multiple db can be divided by ","')
    cmd_parser.add_argument('out', help='output file name with path')
    cmd_parser.add_argument('-t', '--backupTime', help='every day backup time, 24 hours. Multiple time can be divided by ","')
    cmd_parser.add_argument('-l', '--log', metavar='log.txt', help='log file name')
    cmd_parser.add_argument('-m', '--mode', help='running mode: test/release')

    args = cmd_parser.parse_args(argv[1:])
    log_initialize(args)

    try:
        backup_dbs = []
        if(args.db):
            backup_dbs = args.db.split(',');
            LOG.info('{0} the dbs need backup {1}'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), backup_dbs))
        else:
            LOG.info('{0} backup all dbs'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    except Exception as e:
        LOG.critical('input db name parse error')
        quit_application(-1)
        
    try:
        backup_time_slots = ['20:00']#default
        if(args.backupTime):
            backup_time_slots = args.backupTime.split(',')
            LOG.info('{0} backup time slot {1}'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), backup_time_slots))
        else:
            LOG.info('{0} backup time slot set to 20:00 UTF+8 as default'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))           
    except Exception as e:
        LOG.critical('input backupTime parse error')
        quit_application(-1)

    while(True):
        time_now = datetime.now().strftime('%H:%M')#24 hours format
        LOG.info('{0} backup time checking'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))           
        if(time_now in backup_time_slots):
            LOG.info('{0} start backup...'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            output_dir = ''.join([args.out, '_', datetime.now().strftime('%Y-%m-%d_%H-%M')])

            for db in backup_dbs:
                out = ''.join([output_dir, '\\', db, '.sql'])
                backup_cmd = MYSQL_BACKUP_CMD.format(port=args.port, host=args.host, user=args.user, password=args.password, database=db, output=out)
                process_cmd(backup_cmd, args.mode)

            time.sleep(60)#in case the backup process less than 1 min
        else:
            time.sleep(60)#start another round of checking after 1 min


if __name__=='__main__':
    main(sys.argv)
