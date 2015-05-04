import jenkins
import xml.etree.ElementTree as ET



def main():
    try:
        j = jenkins.Jenkins('http://xxx-test-ci.eng.citrite.net:8080', 'username_ci', 'password_ci')
        jobs = j.get_jobs()
        cfg_xml_origin = j.get_job_config("Config-RfAndroid-RfAndroid-Main")
        root = ET.fromstring(cfg_xml_origin)
        tree = ET.ElementTree(root)
        
        #get parameters for scm p4 settings at job configuration file
        for scm in root.findall('scm'):
            p4User = scm.find('p4User').text
            p4Passwd = scm.find('p4Passwd').text
            p4Port = scm.find('p4Port').text
            projectPath = scm.find('projectPath').text
            
            
        #set parameter
        for scm in root.findall('scm'):
             scm.find('projectPath').text = '//localization/LocEngineering/LocEngg-Tools/BeaconToolConfig/DesktopAndApps/RfAndroid/RfAndroid/Main/... //Beacon-Test-Config-RfAndroid-RfAndroid-Main/src/...\n//localization/LocEngineering/LocEngg-Tools/BeaconToolConfig/DesktopAndApps/RfAndroid/RfAndroid/Main/... //Beacon-Test-Config-RfAndroid-RfAndroid-Main/src/...\n//localization/LocEngineering/LocEngg-Tools/BeaconToolConfig/DesktopAndApps/RfAndroid/RfAndroid/Main/... //Beacon-Test-Config-RfAndroid-RfAndroid-Main/src/...\n//localization/LocEngineering/LocEngg-Tools/BeaconToolConfig/DesktopAndApps/RfAndroid/RfAndroid/Main/... //Beacon-Test-Config-RfAndroid-RfAndroid-Main/src/...'
        cfg_xml_dst = ET.tostring(root, encoding='utf-8', method='xml')
        #print(cfg_xml_dst)
        #re-config job
        j.reconfig_job('Config-RfAndroid-RfAndroid-Main', cfg_xml_dst)
         
    except Exception as e:
        print(e);     
    

if __name__=="__main__":
    main();