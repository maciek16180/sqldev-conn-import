import sys

from xml.etree import ElementTree


if __name__ == '__main__':
    assert len(sys.argv) > 1, 'Input file not provided.'

    fname = sys.argv[1]
    input_root = ElementTree.parse(fname).getroot()

    for ds in input_root.findall('data-source'):
        user = ds.find('connection').get('user')

        if ds.find('filters') is not None:
            print('Connection [', ds.get('name'), '] already has a filter set up. Skipping...')
            continue
        if user in ('sys', 'system'):
            print('Skipping setting a filter on [', ds.get('name'), ']')
            continue

        print('    Setting default filter for [', ds.get('name'), ']')
        filters = ElementTree.SubElement(ds, 'filters')
        filter_ = ElementTree.SubElement(filters, 'filter', type='org.jkiss.dbeaver.ext.oracle.model.OracleSchema')
        ElementTree.SubElement(filter_, 'include', name=user.upper())

    ElementTree.ElementTree(input_root).write(fname + '.backup', encoding="utf-8", xml_declaration=True)
    ElementTree.ElementTree(input_root).write(fname, encoding="utf-8", xml_declaration=True)

