import spacy
from spacy.tokens import DocBin
from tqdm import tqdm # Affichage d'une barre de progression
import difflib # Recherche de similarité entre deux chaînes de caractères
import pandas as pd

from spacy.language import Language
from spacy_langdetect import LanguageDetector

# Import des fonctions personnalisées qui seront utilisées dans ce notebook
from ..modules_nlp.process_departure_destination import departure_destination

# Chargement du modèle entrainé "model-best" situé deux dossiers plus haut
nlp_itineraire = spacy.load("NLP/model-best/")


# Chargement du modèle Français medium - Ce modèle sera utilisé pour la détection des langues
nlp_fr = spacy.load("fr_core_news_md")



@Language.factory('language_detector')
def language_detector(nlp, name):
    return LanguageDetector()

# Ajouter LanguageDetector à la pipeline si ce n'est pas déjà le cas
if 'language_detector' not in nlp_fr.pipe_names:
    # print("Ajout de LanguageDetector à la pipeline")
    nlp_fr.add_pipe('language_detector', last=True)
    # print("LanguageDetector ajouté à la pipeline")

fichier_villes = 'NLP/liste_villes_500.txt'

class EntityRecognitionService:
    # def __init__(self):
        # self.nlp = spacy.load("fr_core_news_md")
        

    def extract_loc(self, text: str) -> list:
        """Extracts locations from a text.

        Args:
            text (str): Text to extract locations from

        Returns:
            list: List of locations. Departure is first, destination is second
        """
        # depart = None
        # destination = None

        # for token in self.nlp(text):
        #     # Si le token est de type LOC, on analyse les tokens enfants pour déterminer s'il s'agit d'une préposition (case) et si oui, laquelle (de, à, depuis, etc.
        #     if token.ent_type_ in ["LOC"]:
        #         for subtoken in token.children :
        #             if(subtoken.dep_ == "case"):
        #                 # Si c'est une préposition de départ
        #                 if(subtoken.text in ["de", "depuis"]):
        #                     depart = token.text
        #                 # Si c'est une préposition de destination
        #                 elif(subtoken.text in ["à", "vers"]):
        #                     destination = token.text


        try:
            depart, destination = departure_destination(text, nlp_fr, nlp_itineraire, fichier_villes)
        except Exception as e:
            print("Extraction des entités impossible")
            exit()



        return depart, destination