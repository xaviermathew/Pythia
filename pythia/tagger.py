import functools
import itertools
import logging

from pythia.graph_utils import find_nodes_for_entity, find_centroid, score_combination
from pythia.text_utils import find_entities

_LOG = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)
DUMMY_ENTITY_SEARCH_RESULTS = [(None, 0.0)]


def tag(G, query):
    entity_map = find_entities(query)
    node_map = {}
    for entity in entity_map:
        entities = find_nodes_for_entity(G, entity)
        if not entities:
            entities = DUMMY_ENTITY_SEARCH_RESULTS
        node_map[entity] = entities
        _LOG.debug('entity:%s candidates:%s', entity, node_map[entity])
    combinations = list(itertools.product(*node_map.values()))
    scorer = functools.partial(score_combination, G)
    best = max(combinations, key=scorer)
    resolved_entity_map = {}
    for i, entity in enumerate(node_map):
        if best[i][0] is not None:
            resolved_entity_map[entity] = best[i]
    resolved_entities = [node for node, score in resolved_entity_map.values()]
    for entity, spacy_types in entity_map.items():
        if entity not in resolved_entity_map:
            resolved_entity_map[entity] = find_centroid(G, resolved_entities, spacy_types=spacy_types)
    return resolved_entity_map
