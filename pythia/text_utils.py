import logging

import spacy

from pythia.node_types import Person, Place, Organization

_LOG = logging.getLogger(__name__)
NLP = None
QUESTION_TOKENS = {
    'who': {Person},
    'where': {Place, Organization},
}


def get_spacy_types_for_node_types(node_types):
    return {spacy_type
            for node_type in node_types
            for spacy_type in node_type.spacy_types if spacy_type != 'NP'}


def jaccard_score(s1, s2):
    s1 = set(s1.lower().split())
    s2 = set(s2.lower().split())
    sinter = s1.intersection(s2)
    sunion = s1.union(s2)
    return 1.0 * len(sinter)/len(sunion)


def find_entities(query):
    global NLP

    if NLP is None:
        NLP = spacy.load('en_core_web_sm')

    named_entities = NLP(unicode(query))
    entity_map = {}
    for ent in named_entities.ents:
        _LOG.debug('text:%s label:%s', ent.text, ent.label_)
        entity_map[ent.text] = {ent.label_}
    def is_already_found(ent):
        for token in ent.text.split():
            if token in entity_map or [1 for entity in entity_map if entity in token]:
                return True
        return False
    for ent in named_entities.noun_chunks:
        if ent.text not in entity_map and not is_already_found(ent):
            _LOG.debug('text:%s label:%s', ent.text, ent.label_)
            entity_map[ent.text] = {ent.label_}
    for t in named_entities:
        t_lower = t.text.lower()
        if t_lower in QUESTION_TOKENS:
            entity_map[t.text] = get_spacy_types_for_node_types(QUESTION_TOKENS[t_lower])
    return entity_map
