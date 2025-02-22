import xml.etree.ElementTree as ET

def robust_validate_and_correct_xml(input_file, output_file):
    """
    Valida e corrige um arquivo XML, remove caracteres inválidos e corrige a estrutura.
    """
    try:
        # tratar caracteres inválidos
        with open(input_file, 'r', encoding='utf-8') as file:
            raw_content = file.read()

        # Substituir caracteres inválidos 
        clean_content = raw_content.replace('%', '')  # Remove '%'
        clean_content = clean_content.replace('&', '&amp;')  # Escapa '&'

        # Reprocessa o conteúdo limpo como XML
        root = ET.fromstring(clean_content)
        tree = ET.ElementTree(root)

        # Remove espaços em branco 
        for elem in root.iter():
            if elem.text:
                elem.text = elem.text.strip()
            if elem.tail:
                elem.tail = elem.tail.strip()

        # Guarda o XML corrigido
        tree.write(output_file, encoding="utf-8", xml_declaration=True)
        print(f"XML corrigido salvo em: {output_file}")
        return True

    except ET.ParseError as e:
        print(f"Erro ao processar o XML: {e}")
        return False

# Caminhos dos arquivos
input_xml = r"C:\Users\jorge\OneDrive\Ambiente de Trabalho\Engenharia Informatica\3ºAno\IS\Is-final\data\media\output.xml"
output_xml = r"C:\Users\jorge\OneDrive\Ambiente de Trabalho\Engenharia Informatica\3ºAno\IS\Is-final\data\media\final_corrected_output.xml"

# Validar e corrigir
if robust_validate_and_correct_xml(input_xml, output_xml):
    print("XML corrigido com sucesso!")
else:
    print("O XML ainda contém problemas.")
