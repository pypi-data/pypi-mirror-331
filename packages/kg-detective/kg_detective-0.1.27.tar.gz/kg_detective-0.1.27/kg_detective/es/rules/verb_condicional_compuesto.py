from spacy.matcher import Matcher, DependencyMatcher
from kg_detective.lib import clean_merge, mark

def search_out(doc, nlp):
  """Search for  

  Args:
    doc (spacy.tokens.Doc): doc to be analyzed
    nlp (spacy.language.Language): context language

  Returns:
    list: list of spacy.tokens.Span
  """

  patterns = [
    [{"POS": "AUX", "DEP": "aux", "MORPH": {"IS_SUPERSET": ["Mood=Cnd", "VerbForm=Fin"]}, "LEMMA": "haber"}, {"POS": {"IN": ["VERB", "AUX"]}, "MORPH": {"IS_SUPERSET": ["Tense=Past", "VerbForm=Part"]}}],
  ]

  raw_matches = []

  rule_name = "verb_condicional_compuesto"

  return [] 
   
