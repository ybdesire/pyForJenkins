from openpyxl import load_workbook
from xml.etree.ElementTree import Element, SubElement, tostring, XML
from xml.etree import ElementTree
from xml.dom import minidom

PRODUCT_OWNER_LIST_FILE = 'list.xlsx'

def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ElementTree.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")
       
class XMLCreator:
    def __init__(self):
        self.sheet_ranges=None
        self.column_length=None

    def read_product_owner_info(self):
        wb = load_workbook(PRODUCT_OWNER_LIST_FILE)
        self.sheet_ranges = wb['Sheet1']
        self.column_length = int(self.sheet_ranges.dimensions.split(':')[1].split('C')[1]) 
       
    def get_products_names_list(self):
        if(self.sheet_ranges==None):
            self.read_product_owner_info()
        products = []
        for i in range(2, self.column_length+1):
            index = str(i)
            products.append(self.sheet_ranges['A'+index].value.split('-')[0])
        return list(set(products))
    
    def get_component_list_from_product(self, product):  
        if(self.sheet_ranges==None):
            self.read_product_owner_info()
        components=[]
        for i in range(2, self.column_length+1):
            index = str(i)
            if(self.sheet_ranges['A'+index].value.split('-')[0]==product):
                components.append(self.sheet_ranges['A'+index].value.split('-')[1])
        return list(set(components))
    
    def get_branch_list_from_product_and_component(self, product, component):    
        if(self.sheet_ranges==None):
            self.read_product_owner_info()
        branch_list=[]
        for i in range(2, self.column_length+1):
            index = str(i)
            if((product==self.sheet_ranges['A'+index].value.split('-')[0]) and (component==self.sheet_ranges['A'+index].value.split('-')[1])):
                branch_and_suppli = self.sheet_ranges['A'+index].value.replace('{0}-{1}-'.format(product, component), '')
                branch_list.append(branch_and_suppli)
        return list(set(branch_list))

    def get_owner_names_of_product(self, product):
        if(self.sheet_ranges==None):
            self.read_product_owner_info()
        owner_list=[]
        for i in range(2, self.column_length+1):
            index = str(i)
            if(product==self.sheet_ranges['A'+index].value.split('-')[0]):
                owner_list.append(self.sheet_ranges['B'+index].value)
        return list(set(owner_list))
      
    def get_owner_names_of_component(self, product, component):
        if(self.sheet_ranges==None):
            self.read_product_owner_info()
        owner_list=[]
        for i in range(2, self.column_length+1):
            index = str(i)
            if(product==self.sheet_ranges['A'+index].value.split('-')[0] and component==self.sheet_ranges['A'+index].value.split('-')[1]):
                owner_list.append(self.sheet_ranges['B'+index].value)
        return list(set(owner_list))
    
    def get_owner_name_of_branch(self, product, component, branch):
        if(self.sheet_ranges==None):
            self.read_product_owner_info()
        owner_list=[]
        for i in range(2, self.column_length+1):
            index = str(i)
            if('{0}-{1}-{2}'.format(product, component, branch)==self.sheet_ranges['A'+index].value):
                owner_list.append(self.sheet_ranges['B'+index].value)
        return list(set(owner_list))[0]
    
    def get_owner_email_by_name(self, name):
        if(self.sheet_ranges==None):
            self.read_product_owner_info()
        email_list=[]
        for i in range(2, self.column_length+1):
            index = str(i)
            if(name == self.sheet_ranges['B'+index].value):
                email_list.append(self.sheet_ranges['C'+index].value)
        return list(set(email_list))[0]
    
    def get_xml_content(self):
        top=Element('products')
        products = self.get_products_names_list()
        for product in products:
            ele_product = SubElement(top, 'product', name=product)
            product_owner_names = self.get_owner_names_of_product(product)
            product_level_elements = False
            if(len(product_owner_names)==1):
                ele_owners = SubElement(ele_product, 'owners')
                ele_product_owner_names = SubElement(ele_owners, 'owner', name=product_owner_names[0])
                ele_product_owner_names.text = self.get_owner_email_by_name(product_owner_names[0])
                
                ele_thresholds = SubElement(ele_product, 'checkingThresholds')
                ele_threshold_issue_count = SubElement(ele_thresholds, 'issueCount')
                ele_threshold_issue_increase_rate = SubElement(ele_thresholds, 'issueIncreaseRate')
                ele_threshold_issue_decrease_rate = SubElement(ele_thresholds, 'issueDecreaseRate')
                ele_threshold_issue_count.text = '500'
                ele_threshold_issue_increase_rate.text = '0.3'
                ele_threshold_issue_decrease_rate.text = '0.5'
                product_level_elements = True
            components = self.get_component_list_from_product(product)
            for component in components:
                component_owner_names = self.get_owner_names_of_component(product, component)
                ele_component = SubElement(ele_product, 'component', name=component)
                component_level_elements = False
                if(len(component_owner_names)==1 and not product_level_elements):
                    ele_owners = SubElement(ele_component, 'owners')
                    ele_component_owner_names = SubElement(ele_owners, 'owner', name=component_owner_names[0])
                    ele_component_owner_names.text = self.get_owner_email_by_name(component_owner_names[0])
                    
                    ele_thresholds = SubElement(ele_component, 'checkingThresholds')
                    ele_threshold_issue_count = SubElement(ele_thresholds, 'issueCount')
                    ele_threshold_issue_increase_rate = SubElement(ele_thresholds, 'issueIncreaseRate')
                    ele_threshold_issue_decrease_rate = SubElement(ele_thresholds, 'issueDecreaseRate')
                    ele_threshold_issue_count.text = '500'
                    ele_threshold_issue_increase_rate.text = '0.3'
                    ele_threshold_issue_decrease_rate.text = '0.5'
                    component_level_elements = True

                branchs = self.get_branch_list_from_product_and_component(product, component)
                for branch in branchs:
                    branch_owner_name = self.get_owner_name_of_branch(product, component, branch)
                    ele_branch = SubElement(ele_component, 'branch', name=branch)
                    if not (product_level_elements or component_level_elements):
                        ele_owners = SubElement(ele_branch, 'owners')
                        ele_branch_owner_names = SubElement(ele_owners, 'owner', name=branch_owner_name)
                        ele_branch_owner_names.text = self.get_owner_email_by_name(branch_owner_name)
                        
                        ele_thresholds = SubElement(ele_branch, 'checkingThresholds')
                        ele_threshold_issue_count = SubElement(ele_thresholds, 'issueCount')
                        ele_threshold_issue_increase_rate = SubElement(ele_thresholds, 'issueIncreaseRate')
                        ele_threshold_issue_decrease_rate = SubElement(ele_thresholds, 'issueDecreaseRate')
                        ele_threshold_issue_count.text = '500'
                        ele_threshold_issue_increase_rate.text = '0.3'
                        ele_threshold_issue_decrease_rate.text = '0.5'
                    else:
                        ele_branch.text=''
                    #print('{0}-{1}-{2}:{3}, {4}'.format(product, component, branch, owner_name, owner_email))
                #print('{0}-{1}:{2}'.format( product, component, branchs ))
        return top
    
def main():
    creator = XMLCreator()
    top = creator.get_xml_content()
    print(prettify(top))
    
if __name__=='__main__':
    main()