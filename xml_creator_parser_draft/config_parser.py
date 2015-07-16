#! /usr/bin/env python
# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET
from collections import defaultdict

class CfgParser:
    def __init__(self, filename):
        self.cfg_file_name = filename
        self.cfg_xml = None
        self.cfg_xml_root = None
        
        self.project_list = []
        self.email_list_of_project = {}#d[project]=[]
        self.owner_name_of = defaultdict(defaultdict)#d[project][email] = name
        self.threshold_issue_count_of_project = {}
        self.threshold_issue_increase_rate_of_project = {}
        self.threshold_issue_decrease_rate_of_project = {}
        
    def get_cfg_handle(self):
        if self.cfg_xml==None:
            tree = ET.parse(self.cfg_file_name)
            self.cfg_xml_root = tree.getroot()
            self.cfg_xml = ET.tostring(self.cfg_xml_root, encoding='utf-8', method='xml')
    
    def get_project_name_list(self):
        self.get_cfg_handle()
        projects_list=[]
        for product in self.cfg_xml_root:
            for component in product.findall('component'):
                for branch in component.findall('branch'):
                    projects_list.append('{0}-{1}-{2}'.format(product.attrib['name'].strip(), component.attrib['name'].strip(), branch.attrib['name'].strip()))
        return list(set(projects_list))            
    
    def get_owner_email_list_from_element(self, element):
        email=[]
        for owners in element.findall('owners'):
            for owner in owners.findall('owner'):
                email.append(owner.text.strip())
        return list(set(email))
    
    def get_project_owner_email_list(self, project):
        self.get_cfg_handle()
        
        prj_product_name = project.split('-')[0]
        prj_component_name = project.split('-')[1]
        prj_branch_name = project.replace('{0}-{1}-'.format(prj_product_name, prj_component_name), '')
        
        project_owner_email_list=[]
        
        for product in self.cfg_xml_root:
            if(product.attrib['name'].strip()==prj_product_name):
                project_owner_email_list = project_owner_email_list + self.get_owner_email_list_from_element(product)
                for component in product.findall('component'):
                    if(component.attrib['name'].strip()==prj_component_name):
                        project_owner_email_list = project_owner_email_list + self.get_owner_email_list_from_element(component)
                        for branch in component.findall('branch'):
                            if(branch.attrib['name'].strip()==prj_branch_name):
                                project_owner_email_list = project_owner_email_list + self.get_owner_email_list_from_element(branch)
        return list(set(project_owner_email_list))
 
    def get_owner_name_from_element(self, element, email):
        for owners in element.findall('owners'):
            for owner in owners.findall('owner'):
                if(email==owner.text.strip()):
                    return owner.attrib['name'].strip()
                
        return False
    
    def get_owner_name(self, project, owner_email):
        self.get_cfg_handle()
        
        prj_product_name = project.split('-')[0]
        prj_component_name = project.split('-')[1]
        prj_branch_name = project.replace('{0}-{1}-'.format(prj_product_name, prj_component_name), '')
        
        owner_name=None
        for product in self.cfg_xml_root:
            if(product.attrib['name'].strip()==prj_product_name):
                owner_name = self.get_owner_name_from_element(product, owner_email)
                if(owner_name):
                    return owner_name                
                for component in product.findall('component'):
                    if(component.attrib['name'].strip()==prj_component_name):  
                        owner_name = self.get_owner_name_from_element(component, owner_email)
                        if(owner_name):
                            return owner_name  
                        for branch in component.findall('branch'):
                            if(branch.attrib['name'].strip()==prj_branch_name):
                                owner_name = self.get_owner_name_from_element(component, owner_email)
                                if(owner_name):
                                    return owner_name  
        return owner_name
    
    def get_thresholds_from_element(self, element):
        thresholds = {}
        
        for ele_threshold in element.findall('checkingThresholds'):
            thresholds['issueCount'] = ele_threshold.find('issueCount').text.strip()
            thresholds['issueIncreaseRate'] = ele_threshold.find('issueIncreaseRate').text.strip()
            thresholds['issueDecreaseRate'] = ele_threshold.find('issueDecreaseRate').text.strip()
        return thresholds
    
    def get_thresholds(self, project):
        self.get_cfg_handle()
        
        prj_product_name = project.split('-')[0]
        prj_component_name = project.split('-')[1]
        prj_branch_name = project.replace('{0}-{1}-'.format(prj_product_name, prj_component_name), '')
        
        thresholds = {}
        
        for product in self.cfg_xml_root:
            if(product.attrib['name'].strip()==prj_product_name):
                temp_thresholds = self.get_thresholds_from_element(product)
                if(len(temp_thresholds)>0):
                    thresholds = temp_thresholds
                for component in product.findall('component'):
                    if(component.attrib['name'].strip()==prj_component_name): 
                        temp_thresholds = self.get_thresholds_from_element(component) 
                        if(len(temp_thresholds)>0):
                            thresholds = temp_thresholds
                        for branch in component.findall('branch'):
                            if(branch.attrib['name'].strip()==prj_branch_name):
                                temp_thresholds = self.get_thresholds_from_element(branch)
                                if(len(temp_thresholds)>0):
                                    thresholds = temp_thresholds
        return thresholds
    
    # return a list of all project name
    
    def getProjectList(self):
        if(len(self.project_list)==0):
            self.project_list = self.get_project_name_list()
        return self.project_list
    
    def getOwnerEmailsOfProject(self, project):
        '''get a email list
           Arg: project, project name, such as XenDesktop-License-Main
        '''
        if(len(self.email_list_of_project)==0):#init self.email_list_of_project by iterate all project
            if(len(self.project_list)==0):
                self.project_list = self.get_project_name_list()
            for project_name in self.project_list:
                email_list = self.get_project_owner_email_list(project_name)
                self.email_list_of_project[project_name] = email_list

        return self.email_list_of_project[project]
    
    def getThresholdIssueCountOfProject(self, project):
        '''get a int value of threshold 'issueCount'
           Arg: project, project name, such as XenDesktop-License-Main
        '''
        if(len(self.threshold_issue_count_of_project)==0):#init by iterate all project
            if(len(self.project_list)==0):
                self.project_list = self.get_project_name_list()
            for project_name in self.project_list:
                thresholds = self.get_thresholds(project_name)
                self.threshold_issue_count_of_project[project_name]=thresholds['issueCount'].strip()
        return int(self.threshold_issue_count_of_project[project])

    def getThresholdIssueIncreaseRateOfProject(self, project):
        '''get a float value of threshold 'issueIncreaseRate'
           Arg: project, project name, such as XenDesktop-License-Main
        '''
        if(len(self.threshold_issue_increase_rate_of_project)==0):#init by iterate all project
            if(len(self.project_list)==0):
                self.project_list = self.get_project_name_list()
            for project_name in self.project_list:
                thresholds = self.get_thresholds(project_name)
                self.threshold_issue_increase_rate_of_project[project_name]=thresholds['issueIncreaseRate'].strip()
        return float(self.threshold_issue_increase_rate_of_project[project])

    def getThresholdIssueDecreaseRateOfProject(self, project):
        '''get a float value of threshold 'issueDecreaseRate'
           Arg: project, project name, such as XenDesktop-License-Main
        '''
        if(len(self.threshold_issue_decrease_rate_of_project)==0):#init by iterate all project
            if(len(self.project_list)==0):
                self.project_list = self.get_project_name_list()
            for project_name in self.project_list:
                thresholds = self.get_thresholds(project_name)
                self.threshold_issue_decrease_rate_of_project[project_name]=thresholds['issueDecreaseRate'].strip()
        return float(self.threshold_issue_decrease_rate_of_project[project])

    def getOwnerName(self, project, email):
        '''get the owner name at project & email
           if there are different owner namers for each project & email, the first found owner name will be returned
        '''
        if(len(self.owner_name_of)==0):
            if(len(self.project_list)==0):
                self.project_list = self.get_project_name_list()
            for project_name in self.project_list:
                email_list = self.getOwnerEmailsOfProject(project_name)
                for email_addr in email_list:
                    owner_name = self.get_owner_name(project_name, email_addr)
                    self.owner_name_of[project_name][email_addr] = owner_name
        return self.owner_name_of[project][email]
    