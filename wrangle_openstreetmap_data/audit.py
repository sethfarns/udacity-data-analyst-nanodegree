import xml.etree.ElementTree as ET
import re
from collections import defaultdict
import pprint

street_type_re = re.compile(r'^\b\S+\.?', re.IGNORECASE)
expected = ["Rua", "Avenida", "Travessa", "Alameda", "Praça"]
mapping = { "Av": "Avenida",
           "Ave": "Avenida",
           "R": "Rua",
           "Tr": "Travessa",
           "Pr": "Praça",
           "Al": "Alameda",
           "Tv": "Travessa"
          }

# checks to see if first word of street name is in the
# expected list; if not, adds to the street_types list
def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)
    return street_types

# checks to see if the tag is a street
def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")


# checks to see if postal codes have the correct
# number of digits and if there are dashes (correct)
# or periods (not correct)
other_postal_codes = set()
def audit_postal_code(postal_codes, postal_code):
    if re.match(r'^\d{5}\-\d{3}$', postal_code):
        postal_codes['dash'] += 1
    elif re.match(r'^\d{8}$', postal_code):
        postal_codes['no_dash'] += 1
    elif re.match(r'^\d{8}$', postal_code.replace(".","")) or re.match(r'^\d{5}\-\d{3}$', postal_code.replace(".","")):
        postal_codes['periods'] += 1
    else:
        postal_codes['other'] += 1
        other_postal_codes.add(postal_code)
    return postal_codes

def is_postal_code(elem):
    return (elem.attrib['k'] == "addr:postcode")


# checks to see if state name is "CE" (correct)
# or Ceará (not correct) or something else
other_state_names = set()
def audit_state_name(state_names, state_name):
    if state_name == "CE":
        state_names["CE"] += 1
    elif state_name == "Ceará":
        state_names["Ceará"] += 1
    else:
        state_names["other"] += 1
        other_state_names.add(state_name)
    return state_names

# identifies if the tag is the state name
def is_state_name(elem):
    return (elem.attrib['k'] == "addr:state")



# examines and categorizes key types
lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
lower_colon_set = set()
house_numbers = set()
problem_chars_set = set()
other_keys = set()
all_keys = set()
def key_type(element, keys):
    if element.tag == "tag":
        if element.attrib['k']:
            all_keys.add(element.attrib['k'])
            if problemchars.search(element.attrib['k']):                
                keys['problemchars'] += 1
                problem_chars_set.add(element.attrib['k'])
            elif lower_colon.search(element.attrib['k']):
                keys['lower_colon'] += 1                
            elif lower.search(element.attrib['k']):                
                keys['lower'] += 1
            else:                
                keys['other'] += 1
                other_keys.add(element.attrib['k'])
    return keys

# runs the audit, with the option to output everything for the user
def audit(osmfile, verbose=False):
    osm_file = open(osmfile, "r", encoding='utf-8')
    street_types = defaultdict(set)
    postal_codes = {"dash": 0, "no_dash": 0, "periods": 0, "other": 0}
    state_names = {"CE": 0, "Ceará": 0, "other": 0}
    keys = {"lower": 0, "lower_colon": 0, "problemchars": 0, "other": 0}
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        keys = key_type(elem, keys)
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    street_types = audit_street_type(street_types, tag.attrib['v'])
                elif is_postal_code(tag):
                    postal_codes = audit_postal_code(postal_codes, tag.attrib['v'])
                elif is_state_name(tag):
                    state_names = audit_state_name(state_names, tag.attrib['v'])
    osm_file.close()
    if verbose == True:
        print("Bad street names (indexed by first word in address):")
        pprint.pprint(dict(street_types))
        print("\nTypes of postal codes seen:")
        pprint.pprint(dict(postal_codes))
        print("Other postal codes seen:")
        pprint.pprint(set(other_postal_codes))
        print("\nTypes of state names seen:")
        pprint.pprint(dict(state_names))
        print("Other state names seen:")
        pprint.pprint(set(other_state_names))
        print("\nKey types seen:")
        pprint.pprint(dict(keys))
        print("Keys with problem characters:")
        pprint.pprint(set(problem_chars_set))
        print("Other keys seen:")
        pprint.pprint(set(other_keys))
        print("All keys seen:")
        pprint.pprint(set(all_keys))