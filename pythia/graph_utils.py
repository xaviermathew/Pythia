import itertools
import logging

import networkx as nx
from networkx.exception import NetworkXNoPath

from pythia.text_utils import jaccard_score

_LOG = logging.getLogger(__name__)


def init_graph(data):
    G = nx.Graph()
    for from_node, rel_type, to_node in data:
        G.add_edge(from_node, to_node, rel_type=rel_type)
    return G


def find_nodes_for_entity(G, entity):
    entity = entity.lower()
    nodes = []
    for node in G.nodes:
        score = jaccard_score(node.name, entity)
        if score > 0:
            nodes.append((node, score))
    return nodes


def get_score(d):
    return (d['nx_score'] * 0.8) + (d['n1_score'] * 0.1) + (d['n2_score'] * 0.1)


def score_combination(G, nodes):
    _LOG.debug('combination:%s', nodes)
    pairs = list(itertools.combinations(nodes, 2))
    scores = []
    for (n1, n1_score), (n2, n2_score) in pairs:
        if n1 == n2:
            continue
        elif n1 is None or n2 is None:
            num_hops = len(G.nodes) + 1
        else:
            try:
                path = nx.shortest_path(G, n1, n2)
            except NetworkXNoPath:
                num_hops = len(G.nodes) + 1
            else:
                num_hops = len(path)
        nx_score = 1.0 - (float(num_hops)/(len(G.nodes) + 1))
        score_d = {
            'nx_score': nx_score,
            'n1_score': n1_score,
            'n2_score': n2_score,
        }
        score = get_score(score_d)
        _LOG.debug('%s[%s] is [%s] close to %s[%s] - score:%s', n1, n1_score, nx_score, n2, n2_score, score)
        scores.append(score)
    return sum(scores)



def dist(G, n1, n2):
    try:
        path = nx.shortest_path(G, n1, n2)
    except NetworkXNoPath:
        num_hops = len(G.nodes) + 1
    else:
        num_hops = len(path)
    # _LOG.debug('n1:%s n2:%s dist:%s', n1, n2, num_hops)
    return num_hops


def centroid_dist(G, candidate, nodes):
    distances = []
    for node in nodes:
        distances.append(dist(G, candidate, node))
    score = sum(distances)
    _LOG.debug('nodes:%s candidate:%s centroid_dist:%s', nodes, candidate, score)
    return score


def find_centroid(G, nodes, max_depth=10, num_stable_runs=5, spacy_types=None):
    curr_depth = 1
    candidates = {}
    for node in nodes:
        candidates[node] = None
    curr_min = None
    curr_min_node = None
    candidate_min_node = None
    candidate_min = None
    new_nodes = set()
    curr_stable_run = 0
    while True:
        for candidate in candidates:
            if candidates[candidate] is None:
                new_nodes.add(candidate)
                candidates[candidate] = centroid_dist(G, candidate, nodes)
        _candidates = filter(lambda x: x[0] not in nodes, candidates.items())
        if spacy_types is not None:
            _candidates = filter(lambda x: x[0].spacy_types.intersection(spacy_types), _candidates)
        if _candidates:
            candidate_min_node, candidate_min = min(_candidates, key=lambda x: x[1])
            _LOG.debug('curr_min:%s[%s] candidate_min:%s[%s]', curr_min_node, curr_min, candidate_min_node, candidate_min)
        if curr_min_node is not None and candidate_min_node is not None:
            if curr_min_node == candidate_min_node:
                curr_stable_run += 1
            else:
                curr_stable_run = 0
            _LOG.debug('curr_stable_run:%s', curr_stable_run)
            if curr_stable_run == num_stable_runs:
                _LOG.debug('achieved num_stable_runs:%s. break', num_stable_runs)
                break
        if curr_min is None:
            curr_min = candidate_min
            curr_min_node = candidate_min_node
        elif curr_min > candidate_min:
            curr_min = candidate_min
            curr_min_node = candidate_min_node
        for node in new_nodes:
            for candidate in G[node]:
                if candidate not in candidates:
                    # _LOG.debug('add candidate:%s neighbour of:%s', candidate, node)
                    candidates[candidate] = None
            new_nodes = set()
        curr_depth += 1
        if curr_depth >= max_depth:
            _LOG.debug('reached max_depth:%s. break', max_depth)
            break
        # elif not new_nodes:
        #     _LOG.debug('no more neighbours. break')
        #     break
    return curr_min_node, curr_min
