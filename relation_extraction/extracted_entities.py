from json import JSONEncoder
from spacy.tokens.token import Token

class ExtractedEncoder(JSONEncoder):
        def default(self, o):
            if type(o) == Token:
                return str(o)
            return o.__dict__

class Relation:
    """Represent a relationship within the text"""
    def __init__(self, subject, relation, attribute, subject_position=-1):
        self.subject = subject
        self.relation = relation
        self.attribute = attribute
#        self.subject_position = subject_position
        
    def __str__(self):
        return "%s > %s > %s" % (self.subject, self.relation, self.attribute)
    
class RelationDetails:
    """Represent 'details' about a relationship"""
    def __init__(self, attribute, relation, subject, subject_position=-1):
        self.attribute = attribute
        self.relation = relation
        self.subject = subject
#        self.subject_position = subject_position
        
    def __str__(self):
        return "%s > %s > %s" % ( self.attribute, self.relation, self.subject)
        

class ParsedParagraph:
    """Class to represent a parsed paragraph"""
    def __init__(self, text, links, bolds):
        self.text = text
        self.links = links
        self.bolds = bolds
        self.relations:list = None
        self.details:list = None