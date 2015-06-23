#! /usr/bin/env python
# -*- coding: utf-8 -*-

'''MongoDB logic backup tool
'''
import sys
import logging
import argparse
import time
from datetime import datetime

__application__ = 'MongoDB logic backup tool'
__version__ = '1.0'

LOG = None

MONGO_BACKUP_CMD_WITHOUT_USER = 'mongodump --host {hostAddr} --port {serverPort} --out {output} '
MONGO_BACKUP_CMD_WITH_USER = 'mongodump --host {hostAddr} --port {serverPort} --user {mongoUser} --password {mongoPassword} --out {output}'

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
        LOG.info(cmd)
    else:
        pass

def main(argv): 
    cmd_parser = argparse.ArgumentParser();
    cmd_parser.add_argument('-v', '--version', action='version', version='{0}'.format(__version__))
    cmd_parser.add_argument('host', help='mongo db server host/ip')
    cmd_parser.add_argument('port', help='mongo db server port')
    cmd_parser.add_argument('out', help='output file name with path')
    cmd_parser.add_argument('-u', '--userName', help='mongo db user name')
    cmd_parser.add_argument('-p', '--password', help='mongo db password')
    cmd_parser.add_argument('-t', '--backupTime', help='every day backup time, 24 hours. Multiple time can be divided by ","')
    cmd_parser.add_argument('-d', '--db', help='db names to be backupped. Multiple db can be divided by ","')
    cmd_parser.add_argument('-l', '--log', metavar='log.txt', help='log file name')
    cmd_parser.add_argument('-m', '--mode', help='running mode: test/release')
    args = cmd_parser.parse_args(argv[1:])
    
    log_initialize(args)
    
    try:
        backupDBs = []
        if(args.db):
            backupDBs = args.db.split(',');
            LOG.info('{0} the dbs need backup {1}'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), backupDBs))
        else:
            LOG.info('{0} backup all dbs'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    except Exception as e:
        LOG.critical('input db name parse error')
        quit_application(-1)
        
    try:
        backupTimes = ['20:00']
        if(args.backupTime):
            backupTimes = args.backupTime.split(',')
            LOG.info('{0} backup time slot {1}'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), backupTimes))
        else:
            LOG.info('{0} backup time slot set to 20:00 UTF+8 as default'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))           
    except Exception as e:
        LOG.critical('input backupTime parse error')
        quit_application(-1)
        
    while(True):
        timeNow = datetime.now().strftime('%H:%M')#24 hours format
        LOG.info('{0} backup time checking'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))           
        if(timeNow in backupTimes):
            LOG.info('{0} backup begin'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            backupCMD = ''
            outputDir = ''.join([args.out, '_', datetime.now().strftime('%Y-%m-%d_%H-%M')])
            if(args.userName):
                backupCMD = MONGO_BACKUP_CMD_WITH_USER.format(hostAddr=args.host, serverPort=args.port, mongoUser=args.userName, mongoPassword=args.password, output=outputDir)
            else:
                backupCMD = MONGO_BACKUP_CMD_WITHOUT_USER.format(hostAddr=args.host, serverPort=args.port, output=outputDir)

            if not backupDBs:#if backupDBs is empty(no specify db input)                
                backupCMD.format(dbName='')
                process_cmd(backupCMD, args.mode)
            else:
                for database in backupDBs:
                    backupCMD = ''.join([backupCMD, ' --db ', database])
                    process_cmd(backupCMD, args.mode)

            time.sleep(60)#in case the backup process less than 1 min
        else:
            time.sleep(60)#start another round of checking after 1 min
    
if __name__ == '__main__':
    main(sys.argv)
    
