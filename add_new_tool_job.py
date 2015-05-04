# !/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import argparse
import logging
import jenkins
import xml.etree.ElementTree as ET


__author__ = "ybdesire@gmail.com"
__application__ = "Jenkins CI P4 new job adding tool"
__version__ = "1.0.0"

LOG = None

class JobManage:
    def __init__(self, arguments):
        self.arguments = arguments
        self.jci=None   #Jenkins CI connection
        self.targetToolList=None
        self.xml_cfg_origin=None
        
    def get_jenkins_handler(self):
        try:
            self.jci = jenkins.Jenkins(self.arguments.ci_url, self.arguments.ci_username, self.arguments.ci_password)
        except Exception as e:
            LOG.critical("jenkins exception: {0}".format(e))
            quit_application(-1)
    
    def get_cfg_origin(self, cfg_file_path):
        try:
            tree = ET.parse(cfg_file_path)#R"new_tool_job_template\config.xml"
            root = tree.getroot()
            self.xml_cfg_origin=ET.tostring(root, encoding='utf-8', method='xml')
        except Exception as e:
            LOG.critical("ElementTree exception: {0}".format(e))
            quit_application(-1)
    
    def get_jobs_by_name(self, job_name):    #name: prefix-name         
        try:
            jobsName=[]
            if self.jci:
                jobs = self.jci.get_jobs()
                for job in jobs:
                    if(job["name"].split("-")[0]==job_name):
                        jobsName.append(job["name"])
                return jobsName         
            else:
                LOG.critical("jenkins handler NONE")
                quit_application(-1)
        except Exception as e:
            LOG.critical("get_jobs_by_name() exception: {0}".format(e))
            quit_application(-1)
            
    def get_job_assignedNode(self, job_name):#job config file distribution build group
        try:
            job_cfg_xml = self.jci.get_job_config(job_name)
            root = ET.fromstring(job_cfg_xml)
            return root.find("assignedNode").text
        except Exception as e:
            LOG.critical("jenkins exception: {0}".format(e))
            quit_application(-1)

    def runAllJobs(self):
        try:
            self.get_jenkins_handler()
            srcJobs = self.get_jobs_by_name("Src")                 #StringCollector is almost the same as StringDetector
            for src_job_name in srcJobs:
                self.jci.build_job(src_job_name, None, src_job_name)
                print("Run job '{jobName}' successfully".format(jobName=src_job_name)) 
        except Exception as e:
            LOG.critical("runAllJobs exception: {0}".format(e))
            quit_application(-1)
            
    def addNewToolSupport_StringCollector(self):
        try:
            self.get_jenkins_handler()
            self.get_cfg_origin(R"new_tool_job_template\config.xml") #get job template
            StringDetectorJobsName = self.get_jobs_by_name("StringDetector")                 #StringCollector is almost the same as StringDetector
            
            #get target jobs name
            targetJobs={}
            for jobname in StringDetectorJobsName:
                targetJobsName = jobname.replace("StringDetector","StringCollector")
                targetJobsGroup = self.get_job_assignedNode(jobname)
                targetJobs[targetJobsName] = targetJobsGroup
            #print(targetJobs)
            
            for jobname in targetJobs:
                job_cfg_xml = self.get_target_job_cfg_stringcollector(jobname, targetJobs[jobname])
                self.jci.create_job(jobname, job_cfg_xml)
                print("Add new job '{jobName}' successfully!".format(jobName=jobname))
        except Exception as e:
            LOG.critical("addNewToolSupport_StringCollector exception: {0}".format(e))
            quit_application(-1)
      
    def get_target_job_cfg_stringcollector(self, job_name, job_assignedNode):
        try:
            
            root = ET.fromstring(self.xml_cfg_origin)
            tree = ET.ElementTree(root)
            # modify cfg template
            
            root.find("assignedNode").text = job_assignedNode
            root.find("authToken").text = job_name
            
            for trigger in root.findall("triggers"):
                innerTrigger = trigger.find("jenkins.triggers.ReverseBuildTrigger")
                for upstream in innerTrigger.findall("upstreamProjects"):
                    upstream.text = job_name.replace("StringCollector", "Toolset")
                    
            root.find("customWorkspace").text = "C:\CI\workspace\{0}".format(job_name.replace("StringCollector", "Src"))
            
            for buildwrap in root.findall("buildWrappers"):
                innerbuildwrap = buildwrap.find("com.datalex.jenkins.plugins.nodestalker.wrapper.NodeStalkerBuildWrapper")
                for job in innerbuildwrap.findall("job"):
                    job.text = job_name.replace("StringCollector", "Src")
            
            target_xml = ET.tostring(root, encoding='utf-8', method='xml')
            return target_xml
        except Exception as e:
            LOG.critical("get_target_job_cfg_stringcollector exception: {0}".format(e))
            quit_application(-1)
             

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
    arg_parser.add_argument("ci_url", help = "Jenkins URL, such as 'http://beacon-test-ci.eng.citrite.net:8080/'")
    arg_parser.add_argument("ci_username", help = "Jenkins username")
    arg_parser.add_argument("ci_password", help = "Jenkins password")
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
    job_mgr = JobManage(arguments)
    job_mgr.addNewToolSupport_StringCollector()
    #job_mgr.runAllJobs()
    return 0



if __name__=="__main__":
    result = main()
    quit_application(result)
