import os
import xml.etree.ElementTree as ET
from xml.dom import minidom

"""
MATSim Bridge Writer
Converts PCRL Charging Solutions into MATSim XML formats.
"""

def indent(elem, level=0):
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

def write_facilities_xml(charging_plan, node_list, output_path="output_facilities.xml"):
    """
    Converts a charging plan (list of stations) to MATSim facilities.xml
    
    Args:
        charging_plan: List of station objects from env_plus/evaluation_framework
        node_list: List of nodes (to look up coordinates if needed)
        output_path: Destination file
    """
    print(f"Generating MATSim facilities file at {output_path}...")
    
    root = ET.Element("facilities")
    root.set("name", "PCRL_Generated_Charging_Stations")

    # Iterate through the plan
    # Each station in plan has structure: [s_pos, s_x, s_dict]
    # s_pos: [node_id, node_data]
    
    for idx, station in enumerate(charging_plan):
        s_pos = station[0]
        node_id = s_pos[0]
        node_data = s_pos[1]
        
        # Coordinates (MATSim expects projected coordinates, usually UTM)
        # Assuming x/y in node_data are already suitable or we use them as is for now
        x = str(node_data['x'])
        y = str(node_data['y'])
        
        # Create Facility
        fac_id = f"cs_{node_id}" # Charging Station ID
        facility = ET.SubElement(root, "facility")
        facility.set("id", fac_id)
        facility.set("x", x)
        facility.set("y", y)
        
        # Add Activity (interaction point)
        activity = ET.SubElement(facility, "activity")
        activity.set("type", "charging_interaction")
        
        # Add Attributes (Capacity/Power)
        # station[1] is the config array [count_type1, count_type2, count_type3]
        s_x = station[1]
        
        attributes = ET.SubElement(facility, "attributes")
        
        # Total Plugs
        attr_plugs = ET.SubElement(attributes, "attribute")
        attr_plugs.set("name", "charging_plugs")
        attr_plugs.set("class", "java.lang.Integer")
        attr_plugs.text = str(sum(s_x))
        
        # Helper string for specific plug types
        attr_desc = ET.SubElement(attributes, "attribute")
        attr_desc.set("name", "charger_configuration")
        attr_desc.set("class", "java.lang.String")
        attr_desc.text = f"{s_x[0]}x7kW,{s_x[1]}x22kW,{s_x[2]}x50kW"

    # Formatting and Write
    indent(root)
    tree = ET.ElementTree(root)
    
    # MATSim XML Header
    with open(output_path, "wb") as f:
        f.write(b'<?xml version="1.0" encoding="utf-8"?>\n')
        f.write(b'<!DOCTYPE facilities SYSTEM "http://matsim.org/files/dtd/facilities_v1.dtd">\n')
        tree.write(f, encoding="utf-8", xml_declaration=False)
        
    print(f"Successfully wrote {len(charging_plan)} stations to {output_path}")

def write_dummy_config_xml(output_path="config_generated.xml", network_file="network.xml", facilities_file="output_facilities.xml"):
    """
    Creates a basic config.xml to run the simulation.
    """
    root = ET.Element("config")
    
    # Network Module
    module_net = ET.SubElement(root, "module")
    module_net.set("name", "network")
    param_net = ET.SubElement(module_net, "param")
    param_net.set("name", "inputNetworkFile")
    param_net.set("value", network_file)
    
    # Facilities Module
    module_fac = ET.SubElement(root, "module")
    module_fac.set("name", "facilities")
    param_fac = ET.SubElement(module_fac, "param")
    param_fac.set("name", "inputFacilitiesFile")
    param_fac.set("value", facilities_file)
    
    # Controler Module
    module_ctrl = ET.SubElement(root, "module")
    module_ctrl.set("name", "controler")
    param_conf = ET.SubElement(module_ctrl, "param")
    param_conf.set("name", "outputDirectory")
    param_conf.set("value", "./output/matsim_run")
    param_iter = ET.SubElement(module_ctrl, "param")
    param_iter.set("name", "lastIteration")
    param_iter.set("value", "1") # Short run for validation
    
    # Formatting and Write
    indent(root)
    tree = ET.ElementTree(root)
    
    with open(output_path, "wb") as f:
        f.write(b'<?xml version="1.0" encoding="utf-8"?>\n')
        f.write(b'<!DOCTYPE config SYSTEM "http://www.matsim.org/files/dtd/config_v2.dtd">\n')
        tree.write(f, encoding="utf-8", xml_declaration=False)

if __name__ == "__main__":
    # Test block
    print("Testing MATSim Bridge...")
    # Mock data
    mock_node = [123, {'x': 105.8, 'y': 21.0}]
    mock_station = [[mock_node, {'x': 105.8, 'y': 21.0}], [1, 2, 0], {}]
    write_facilities_xml([mock_station], [])
