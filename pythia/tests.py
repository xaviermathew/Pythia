from pythia.data import example_data
from pythia.graph_utils import find_centroid, init_graph
from pythia.node_types import Place, Person, Organization, Occupation
from pythia.tagger import tag

G = init_graph(example_data)


def test_centroid_calc(nodes, spacy_types, result):
    centroid, score = find_centroid(G, nodes, spacy_types=spacy_types)
    print centroid, result
    return centroid == result


def test_tagging(query, result):
    entity_map = tag(G, query)
    entity_map = {entity: node for entity, (node, score) in entity_map.items()}
    print entity_map, result
    return entity_map == result


# make sure the __hash__ override works as expected
assert Place('hyderabad') == Place('hyderabad')

assert test_centroid_calc([Person('xavier mathew'), Place('tamilnadu')], None, Person('mathew something'))
assert test_centroid_calc([Person('india'), Place('spain')], None, Person('navarre'))
assert test_centroid_calc([Person('programmer'), Place('india')], {'PERSON'}, Person('ankit arora'))
assert test_centroid_calc([Person('programmer'), Organization('compile')], {'PERSON'}, Person('ankit arora'))
assert test_centroid_calc([Person('programmer'), Organization('compile'), Place('mumbai')], {'PERSON'}, Person('ankit arora'))
assert test_centroid_calc([Person('programmer'), Organization('compile'), Place('tamilnadu')], {'PERSON'}, Person('xavier mathew'))
assert test_centroid_calc([Person('programmer'), Organization('compile'), Place('telengana')], {'PERSON'}, Person('xavier mathew'))
assert test_centroid_calc([Person('priest'), Place('mumbai')], {'PERSON'}, Person('saint francis xavier'))
assert test_centroid_calc([Person('priest'), Place('spain')], {'PERSON'}, Person('saint francis xavier'))
assert test_centroid_calc([Person('priest'), Place('spain'), Place('pamplona')], {'PERSON'}, Person('saint fermin'))

assert test_tagging('Xavier\'s father is from tamilnadu', {'tamilnadu': Place('tamilnadu'), 'Xavier': Person('xavier mathew')})
assert test_tagging('Xavier\'s father Mathew is from tamilnadu', {'Mathew': Person('mathew something'), 'Xavier': Person('xavier mathew'), 'tamilnadu': Place('tamilnadu')})
assert test_tagging('Xavier is from Spain', {'Xavier': Person('saint francis xavier'), 'Spain': Place('spain')})
assert test_tagging('Xavier Mathew is from Mars', {'Xavier Mathew': Person('xavier mathew'), 'Mars': Place('hyderabad')})
assert test_tagging('Who is the best programmer from India', {'the best programmer': Occupation('programmer'), 'Who': Person('ankit arora'), 'India': Place('india')})
assert test_tagging('Who is the best programmer at Compile', {'the best programmer': Occupation('programmer'), 'Compile': Organization('compile'), 'Who': Person('ankit arora')})
assert test_tagging('Who is the engineer from mumbai', {'the engineer': Occupation('engineer'), 'Who': Person('ankit arora'), 'mumbai': Place('mumbai')})
assert test_tagging('Who is the priest that worked in india', {'the priest': Occupation('priest'), 'Who': Person('saint francis xavier'), 'india': Place('india')})
assert test_tagging('Where do Engineer work', {'Where': Place('hyderabad'), 'Engineer': Occupation('engineer')})
assert test_tagging('Where do Engineer work in Bangalore', {'Bangalore': Place('bangalore'), 'Where': Organization('compile'), 'Engineer': Occupation('engineer')})
assert test_tagging('Where do Priest come from', {'Priest': Occupation('priest'), 'Where': Place('javier')})
