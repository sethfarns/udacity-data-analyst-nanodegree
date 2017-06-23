import csv
import codecs
import pprint
import re
import xml.etree.cElementTree as ET

import cerberus

import my_schema

import audit

NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

SCHEMA = my_schema.schema

# Make sure the fields order in the csvs matches the column order in the sql table schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']

def clean_state_name():
    return "Ceará"

# method for cleaning postal codes
def clean_postal_code(postal_code):
    # first, remove the periods
    postal_code = postal_code.replace(".","")
    # if it matches the preferred format, keep it
    if re.match(r'^\d{5}\-\d{3}$', postal_code):
        return postal_code
    # if it's just missing the dash, add the dash
    elif re.match(r'^\d{8}$', postal_code):
        return postal_code[:5] + "-" + postal_code[5:]
    # otherwise return None, which is a key to remove the record altogether
    return None

mapping = { "Av": "Avenida",
           "Ave": "Avenida",
           "R": "Rua",
           "Tr": "Travessa",
           "Pr": "Praça",
           "Al": "Alameda",
           "Tv": "Travessa"
          }

# method for cleaning street names
def clean_street_name(street_name):
    # check to see if first word is in our mapping
    if street_name.split()[0] in mapping.keys():
        # if it is, replace the key with the value, i.e. the abbreviation with the name written out
        return street_name.replace(street_name.split()[0], mapping[street_name.split()[0]])
    return street_name


def get_tags(child, id):
    # if there are problem characters in the tag, or no 'k' attribute
    # return None, which tells the script to ignore the tag
    if PROBLEMCHARS.search(child.attrib['k']) or child.attrib['k'] == None:
        return None
    elif ':' in child.attrib['k']:
        key_value = ":".join(child.attrib['k'].split(':')[1:])
        type_value = child.attrib['k'].split(':')[0]
    else:
        key_value = child.attrib['k']
        type_value = 'regular'
    value = ""
    if audit.is_street_name(child):
        value = clean_street_name(child.attrib['v'])
    elif audit.is_state_name(child):
        value = clean_state_name()
    elif audit.is_postal_code(child):
        value = clean_postal_code(child.attrib['v'])
        if value == None:
            return None
    else:
        value = child.attrib['v']
    return {
        'id': id,
        'key': key_value,
        'value': value,
        'type': type_value
    }


def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    """Clean and shape node or way XML element to Python dict"""

    node_attribs = {}
    node_required = ['id', 'user', 'uid', 'version', 'lat', 'lon', 'timestamp', 'changeset']
    way_attribs = {}
    way_required = ['id', 'user', 'uid', 'version', 'timestamp', 'changeset']
    way_nodes = []
    tags = []  # Handle secondary tags the same way for both node and way elements

    if element.tag == 'node':
        for child in element.iter():
            if child.tag == 'node':
                for key in child.attrib.keys():
                    if key in node_required:
                        node_attribs[key] = child.attrib[key]
            elif child.tag == 'tag':
                added_tag = get_tags(child, node_attribs['id'])
                if added_tag != None:
                    tags.append(added_tag)
        return {'node': node_attribs, 'node_tags': tags}
    elif element.tag == 'way':
        for child in element.iter():
            if child.tag == 'way':
                for key in child.attrib.keys():
                    if key in way_required:
                        way_attribs[key] = child.attrib[key]
            elif child.tag == 'tag':
                added_tag = get_tags(child, way_attribs['id'])
                if added_tag != None:
                    tags.append(added_tag)
            elif child.tag == 'nd':
                way_nodes.append({
                    'id': way_attribs['id'],
                    'node_id': child.attrib['ref'],
                    'position': len(way_nodes)
                })
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}


# ================================================== #
#               Helper Functions                     #
# ================================================== #
def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema"""
    if validator.validate(element, schema) is not True:
        field, errors = next(iter(validator.errors.items()))
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_string = pprint.pformat(errors)
        
        raise Exception(message_string.format(field, error_string))


class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        if row == None:
            return None
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, str) else v) for k, v in row.items()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


# ================================================== #
#               Main Function                        #
# ================================================== #
def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'w') as nodes_file, \
         codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file, \
         codecs.open(WAYS_PATH, 'w') as ways_file, \
         codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file, \
         codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        validator = cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:
                if validate is True:
                    validate_element(el, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])