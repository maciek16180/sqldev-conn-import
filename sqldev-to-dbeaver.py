import sys
import os

from xml.etree import ElementTree

FIELDS = {  # SQLDeveloper name -> (DBeaver name, default)
    'port': ('port', 1521),
    'hostname': ('host', None),
    'sid': ('database', 'orcl'),
    'user': ('user', None)
}


def indent_xml(elem, level=0):  # https://stackoverflow.com/a/33956544
    tab = 4 * ' '
    i = os.linesep + level * tab
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + tab
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent_xml(elem, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


def get_field_value(node, fieldname):
    fields = node.find('RefAddresses').findall('StringRefAddr')
    matching_field = next((x for x in fields if x.get('addrType') == fieldname), None)

    if matching_field is None:
        default = FIELDS[fieldname][1]
        name = node.get('name')
        sys.stdout.write("Missing value of '" + fieldname + "' for [ " + name + ' ]. ')

        if default is None:
            print('Could not insert default value.')
            return None

        print("Using default value ('", default, "')", sep='')
        return default

    return matching_field.find('Contents').text


if __name__ == '__main__':
    assert len(sys.argv) > 2, 'Provide input file and default password.'

    fname = sys.argv[1]
    output_fname = os.path.join(os.path.dirname(os.path.abspath(fname)), 'dbeaver-import.xml')

    input_root = ElementTree.parse(fname).getroot()
    output_root = ElementTree.Element('connections')

    for conn in input_root:
        connection_params = {FIELDS[fieldname][0]: get_field_value(conn, fieldname) for fieldname in FIELDS}
        if any(v is None for v in connection_params.values()):
            print('Connection [', conn.get('name'), '] skipped.')
            continue
        print('    Adding connection [', conn.get('name'), ']')
        connection_params['name'] = conn.get('name')
        connection_params['password'] = sys.argv[2]

        ElementTree.SubElement(output_root, 'connection', **connection_params)

    indent_xml(output_root)
    output_tree = ElementTree.ElementTree(output_root)
    output_tree.write(output_fname, encoding="utf-8", xml_declaration=True)
