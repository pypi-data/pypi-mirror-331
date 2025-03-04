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
    [{"POS": "PRON", "DEP": "obj", "MORPH": {"IS_SUPERSET": ["Case=Acc", "PrepCase=Npr", "PronType=Prs", "Reflex=Yes"]}, "OP": "?"}, {"POS": "AUX", "LEMMA": "haber", "MORPH": {"IS_SUPERSET": ["Mood=Sub", "Tense=Imp", "VerbForm=Fin"]}}, {"POS": {"IN": ["VERB", "AUX"]}, "MORPH": {"IS_SUPERSET": ["Tense=Past", "VerbForm=Part"]}}],
  ]

  raw_matches = []

  rule_name = "verb_subjuntivo_pretérito_pluscuamperfecto"

  return []
   
