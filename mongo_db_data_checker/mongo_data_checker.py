#! /usr/bin/env python
# -*- coding: utf-8 -*-

'''Beacon data checking tool
'''
import logging
import argparse
import sys
import pymongo

__application__ = 'Beacon data checking tool'
__version__ = '1.0'

LOG = None

class Thresholds:
    def __init__(self, count, increaseRate, decreaseRate, KOLC):
        self.issueCount = count
        self.issueIncreaseRate = increaseRate
        self.issueDecreaseRate = decreaseRate
        self.issueKOLC = KOLC

class IssueStatList:
    def __init__(self, count_list, revision_list):
        self.issueCountList = count_list
        self.issueRevisionList = revision_list

class DataChecker:
    def __init__(self, arguments):
        self.args = arguments
        self.db_handle = None
        self.component_names = []

    def init_db_connect(self):
        try:#connect db
            client = pymongo.MongoClient('mongodb://{host}:{port}/'.format(host=self.args.host, port=self.args.port))
            self.db_handle = client[self.args.database]
            #collection = db['AppDNA-AppDNA-Main']
            #print(collection.find()[10])
        except Exception as e:
            LOG.critical('cannot connect to mongodb://{host}:{port}/'.format(host=self.args.host, port=self.args.port))
            LOG.critical(e)
            quit_application(-1)
    
    def get_components_names(self):
        try:
            for collection_name in self.db_handle.collection_names():
                if len(collection_name.split('-'))>=3:#component name should be the format 'productName-componentName-branch-supplimentary'
                    self.component_names.append(collection_name)
        except Exception as e:
            LOG.critical(e)
            quit_application(-1)
    
    def get_thresholds(self, component_name):
        thres = Thresholds(500, 0.4, 0.6, 3)
        return thres
    
    def issue_count_check(self, component_name, collection):
        try:
            toolsLen = len(collection.find()[collection.count()-1]['tools'])#parse latest build data
            toolsData = collection.find()[collection.count()-1]['tools']
            
            errorCount = 0
            warningCount = 0
            
            for i in list(range(int(toolsLen))):
                errorCount = errorCount + int(toolsData[i]['errors'])
                warningCount = warningCount + int(toolsData[i]['warnings'])
            
            thres = self.get_thresholds(component_name)
            
            if(errorCount+warningCount>thres.issueCount):
                LOG.info('{component}: ERROR:{errors}, WARNING:{warnings}, TOTALISSUE:{total}'.format(component = component_name, errors=errorCount, warnings=warningCount, total=errorCount+warningCount))
            #get threshold
            pass
            #email merge and return
            pass
            #quit_application(1)
            pass
        except Exception as e:
            LOG.critical(e)
            quit_application(-1)
    
    def get_issue_statistics_list(self, component_name, collection):
        try:
            issue_count_list=[]
            issue_revision_list=[]
            
            for i in range(collection.count()):
                toolsData = collection.find()[i]['tools']
                toolsLen = len(collection.find()[i]['tools'])
                errorCount = 0
                warningCount = 0
                for j in range(toolsLen):
                    errorCount = errorCount + int(toolsData[j]['errors'])
                    warningCount = warningCount + int(toolsData[j]['warnings'])
                issue_count_list.append(errorCount+warningCount)
                issue_revision_list.append(collection.find()[i]['_id'])
                #LOG.info('{component}: ERROR:{errors}, WARNING:{warnings}'.format(component = component_name, errors=errorCount, warnings=warningCount))
            issue_list = IssueStatList(issue_count_list, issue_revision_list)
            return issue_list
        except Exception as e:
            LOG.critical(e)
            quit_application(-1)

    def checkIssueCount(self):
        try:#iterate collections and data error checking
            self.init_db_connect()
            self.get_components_names()
            
            for component_name in self.component_names:
                dict1 = self.issue_count_check(component_name, self.db_handle[component_name])
        
        
                #dict2 = issueIncreaseDecreaseRateCheck(db[component_names[0]])
        
        except Exception as e:
            LOG.critical(e)
            quit_application(-1)
    
    def checkIssueIncreaseDecreaseRate(self):
        try:#iterate collections and data error checking
            self.init_db_connect()
            self.get_components_names()
            
            for component_name in self.component_names:
                issue_stat_count = self.get_issue_statistics_list(component_name, self.db_handle[component_name])
                for i in range(len(issue_stat_count.issueCountList)):
                    if(i>0 and issue_stat_count.issueCountList[i]-issue_stat_count.issueCountList[i-1]>0.2*issue_stat_count.issueCountList[i-1]):
                        print('{component}: {counts}, {revision}'.format(component=component_name, counts=issue_stat_count.issueCountList[i], revision=issue_stat_count.issueRevisionList[i]))
        
        except Exception as e:
            LOG.critical(e)
            quit_application(-1)

    
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



def main(argv):
    cmd_parser = argparse.ArgumentParser();
    cmd_parser.add_argument('-v', '--version', action='version', version='{0}'.format(__version__))
    cmd_parser.add_argument('host', help='mongo db server host/ip')
    cmd_parser.add_argument('port', help='mongo db server port')
    cmd_parser.add_argument('database', help='mongo db database')
    cmd_parser.add_argument('-l', '--log', metavar='log.txt', help='log file name')
    args = cmd_parser.parse_args(argv[1:])
    
    log_initialize(args)
    print('{0}, {1}, {2}'.format(args.host, args.port, args.database))   
    
    datacheck = DataChecker(args)
    #datacheck.checkIssueCount()   
    datacheck.checkIssueIncreaseDecreaseRate()   

    
if __name__ == '__main__':
    main(sys.argv)