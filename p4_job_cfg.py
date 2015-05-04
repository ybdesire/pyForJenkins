# !/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import argparse
import logging
import jenkins
import xml.etree.ElementTree as ET


__author__ = "ybdesire@gmail.com"
__application__ = "Jenkins CI P4 Job configuration modification tool"
__version__ = "1.0.0"

LOG = None

class JobP4SCMCfgMgr:
    def __init__(self, arguments):
        self.arguments = arguments
        self.cfg_xml_origin = None
        self.cfg_xml_dst = None
        self.jci=None   #Jenkins CI connection
        
        
    def get_job_cfg_xml(self):
        try:
            self.jci = jenkins.Jenkins(self.arguments.ci_url, self.arguments.ci_username, self.arguments.ci_password)
            self.cfg_xml_origin = self.jci.get_job_config(self.arguments.ci_prj_name)
        except Exception as e:
            LOG.critical("jenkins exception: {0}".format(e))
            quit_application(-1)
                        
    def set_job_cfg_xml(self):
        try:
            root = ET.fromstring(self.cfg_xml_origin)
            tree = ET.ElementTree(root)
            
            #get parameter
            for scm in root.findall('scm'):
                if self.arguments.p4User:
                    scm.find('p4User').text = self.arguments.p4User
                if self.arguments.p4Passwd:
                    scm.find('p4Passwd').text = self.arguments.p4Passwd
                if self.arguments.p4Port:
                    scm.find('p4Port').text = self.arguments.p4Port
                if self.arguments.projectPath:
                    scm.find('projectPath').text = self.arguments.projectPath
            
            self.cfg_xml_dst = ET.tostring(root, encoding='utf-8', method='xml')
            self.cfg_xml_dst = "<?xml version='1.0' encoding='UTF-8'?>" + "\n" + self.cfg_xml_dst 
        except Exception as e:
            LOG.critical("ElementTree exception: {0}".format(e))
            quit_application(-1)
        
    def set_job_cfg_to_jenkins(self):
        try:
            self.jci.reconfig_job(self.arguments.ci_prj_name, self.cfg_xml_dst)
        except Exception as e:
            LOG.critical("Jenkins re-config execption: {0}".format(e))
    
    def getJobsName(self, name):
        self.get_job_cfg_xml()
        self.jci.get_jobs()
         
    def setJobCfg(self):
        self.get_job_cfg_xml()
        self.set_job_cfg_xml()
        self.set_job_cfg_to_jenkins()
        
def log_initialize(arguments):
    try:
        global LOG  
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
        quit_application(-1)

 
def parse_arguments():
    arg_parser = argparse.ArgumentParser(description = "Jenkins CI P4 Job configuration modification tool")
    arg_parser.add_argument("ci_url", help = "Jenkins URL, such as 'http://test-ci.eng.citrite.net:8080/'")
    arg_parser.add_argument("ci_username", help = "Jenkins username")
    arg_parser.add_argument("ci_password", help = "Jenkins password")
    arg_parser.add_argument("ci_prj_name", help= "the project name at Jenkins")
    arg_parser.add_argument("--p4User", help = "perforce username")
    arg_parser.add_argument("--p4Passwd", help = "perforce password, please note here only accept encrypted password by Jenkins")
    arg_parser.add_argument("--p4Port", help = "perforce port, such as 2444/1111")
    arg_parser.add_argument("--projectPath", help = "perforce view-map")    
    arg_parser.add_argument("-g", "--get", help = "get project information, eg: -g cfg/paras/jobs")
    arg_parser.add_argument("-l", "--log", metavar = "log.txt", help = "specify the log file")
    return arg_parser.parse_args()


def quit_application(status):  
    if(status==-1):
        LOG.info("{application} exited abnormally".format(application=__application__))
    else:
        LOG.info("{application} exited normally".format(application=__application__))
    sys.exit(status)

def main():
    arguments= parse_arguments()
    log_initialize(arguments)
    cfg_manage = JobP4SCMCfgMgr(arguments)
    cfg_manage.setJobCfg()
    return 0


def test():
    arguments= parse_arguments()
    printArgument("ci_url", arguments.ci_url)
    printArgument("ci_username", arguments.ci_username)
    printArgument("ci_password", arguments.ci_password)
    printArgument("p4user", arguments.p4user)
    printArgument("p4passwd", arguments.p4passwd)
    printArgument("p4port", arguments.p4port)
    printArgument("project_path", arguments.project_path)
    return 0

def printArgument(name, value):
    if value:
        print("{0} is {1}".format(name, value))
    else:
        print("{0} is none".format(name))

if __name__=="__main__":
    result = main()
    quit_application(result)
