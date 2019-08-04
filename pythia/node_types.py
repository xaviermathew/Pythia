class Node(object):
    spacy_types = {'NP'}

    def __init__(self, name):
        self.name = name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __repr__(self):
        return '<%s:%s>' % (self.__class__.__name__, self.name)


class Person(Node):
    spacy_types = {'NP', 'PERSON'}


class Place(Node):
    spacy_types = {'NP', 'GPE', 'LOC'}


class Organization(Node):
    spacy_types = {'NP', 'ORG'}


class Occupation(Node):
    spacy_types = {'NP'}
