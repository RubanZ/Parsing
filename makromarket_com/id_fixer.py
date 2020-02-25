import sys

from lxml import etree


def fix_ids(xml):
    companies = {}
    tree = etree.fromstring(xml)
    for company in tree.findall('company'):
        name = company.find('name').text.encode('utf-8')
        address = company.find('address').text.encode('utf-8')
        key = (name, address)
        if key not in companies:
            companies[key] = 1
        else:
            companies[key] += 1
        company_id_element = company.find('company-id')
        if company_id_element is not None:
            company_id_element.text = str(companies[key])
    return etree.tostring(tree, encoding='utf-8')


if __name__ == '__main__':
    xml = sys.stdin.read()
    new_table = fix_ids(xml)
    print new_table
