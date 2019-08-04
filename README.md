# Pythia
 Named entity tagging and disambiguation using a Knowledge Graph


## How does this work
1) Initializes a Knowledge Graph into a [NetworkX](https://github.com/networkx/networkx) Graph object
1) Given an input query, uses [spaCy](https://github.com/explosion/spaCy) to identify named entities and noun chunks. Also identifies "question" tokens like "Who" and "Where"
2) For each identified entity, queries the Knowledge Graph to find candidate nodes that have a similar name (using Jaccard similarity)
3) Generates all combinations of candidates and finds the best combination using a weighted sum of graph score (80%) and jaccard similarity score (20%)
4) Graph score is used to represent how closely a given set of nodes/concepts are related. It is calculated as the sum of the lengths of the shortest paths between all nodes in a given combination
5) Out-of-vocabulary entities (and "question" tokens) are calculated as the centroid of all the other resolved entities (filtering candidates based on the entity label identified by spaCy)



## Known issues
* The text similarity scoring (jaccard) is very dumb right now and doesn't do any stemming/lemmatization or handle typos/variations of spellings
* On massive graphs, steps (2) and (5) above are going to take a long time


## Instructions
1) Clone this repo
2) Load example data into the Knowledge Graph or (load your own data using `pythia.graph_utils.init_graph`)
```python
>>> from pythia.data import example_data
>>> from pythia.graph_utils import init_graph
>>> from pythia.tagger import tag
>>> G = init_graph(example_data)
```
3) Start tagging queries
```python
>>> tag(G, "Xavier's father is from tamilnadu")
{u'Xavier': (<Person:xavier mathew>, 0.5),
 u'tamilnadu': (<Place:tamilnadu>, 1.0)}
>>> tag(G, 'Xavier from spain')
{u'Xavier': (<Person:saint francis xavier>, 0.3333333333333333),
 u'spain': (<Place:spain>, 1.0)}
>>> tag(G, 'Who is the priest that worked in india')
{u'Who': (<Person:saint francis xavier>, 8),
 u'india': (<Place:india>, 1.0),
 u'the priest': (<Occupation:priest>, 0.5)}
```
