import lxml 
from lxml import etree

xml_file = "final_corrected_output.xml"

try:
    with open(xml_file, 'r', encoding='utf-8') as file:
        xml_content = file.read()
    etree.fromstring(xml_content)
    print("XML está bem formado.")
except etree.XMLSyntaxError as e:
    print(f"Erro de sintaxe no XML: {e}")