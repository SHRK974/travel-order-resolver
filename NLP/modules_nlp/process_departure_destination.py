import spacy
from spacy.tokens import DocBin
from tqdm import tqdm # Affichage d'une barre de progression
import difflib # Recherche de similarité entre deux chaînes de caractères
import pandas as pd

# -------------------------------------------------------------------------------
# Fonction pour identier les NER "DEPARTURE" et "DESTINATION" d'un texte
# -------------------------------------------------------------------------------
def extract_departure_destination(text, nlp_lang, nlp_itineraire, verbose=True):

    # Transformation du texte en doc avec le modèle fr et le modèle itineraire
    doc_fr = nlp_lang(text)
    doc_itineraire = nlp_itineraire(text)

    # Affichage des entités nommées
    if verbose:
        print("NER originaux : ")
        spacy.displacy.render(doc_fr, style='ent', jupyter=True)
        print("NER itineraire : ")
        spacy.displacy.render(doc_itineraire, style='ent', jupyter=True)
        print("-----------------------------")

    # Initialiser les variables pour stocker les entités "DEPARTURE" et "DESTINATION" ou les erreurs
    departure = None
    destination = None
    itineraire = {}

    # Si la phrase n'est pas en français, on retourne NOT_FRENCH
    if doc_fr._.language['language'] != 'fr':
        return "NOT_FRENCH"

    # Parcourir les entités extraites par spaCy et récupérer les entités "DEPARTURE" et "DESTINATION"
    for ent in doc_itineraire.ents:
        if ent.label_ == "DEPARTURE":
            departure = ent.text
        elif ent.label_ == "DESTINATION":
            destination = ent.text

    # Si on n'a pas trouvé les entités "DEPARTURE" ou "DESTINATION"
    if departure is None or destination is None:
        return "NOT_TRIP"
    else:
        itineraire['departure'] = departure
        itineraire['destination'] = destination

    # Retourner les résultats
    return itineraire

# -------------------------------------------------------------------------------
# Fonction pour traiter un jeu de données et retourner les triplets id, départ, destination
# -------------------------------------------------------------------------------
def process_dataset(file_path, nlp_lang, nlp_itineraire, verbose):
    # Lire le fichier texte
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    outputTriplets = []
    # Traitement de chaque ligne du jeu de données
    for line in lines:
        # Extraire l'ID, les entités "DEPARTURE" et "DESTINATION"
        line_parts = line.strip().split(',', 1)  # Séparer l'ID du reste
        # Si l'ID n'est pas un nombre, on met 0
        file_id = line_parts[0] if line_parts[0].isdigit() else 0
        # Si la deuxième partie n'est pas vide, on l'affecte à text, sinon on récupère la première partie (pas d'id)
        text = line_parts[1] if len(line_parts) > 1 else line_parts[0]

        # Extraction des entités "DEPARTURE" et "DESTINATION"
        itineraire = extract_departure_destination(text, nlp_lang, nlp_itineraire)

        #  Formatage des outputs
        if itineraire == "NOT_FRENCH" or itineraire == "NOT_TRIP":
            # print(f"{file_id},{itineraire}")
            # Ajout à outputTriplets
            # ex.: '5,NOT_TRIP',
            outputTriplets.append(f"{file_id},{itineraire}")
        else:
            # print(f"{file_id},{itineraire['departure']},{itineraire['destination']}")
            # Ajout à outputTriplets
            outputTriplets.append(f"{file_id},{itineraire['departure']},{itineraire['destination']}")  # ex.: '3,Bordeaux,Tours',

    if verbose:
        print("Triplets extraits : ")
        print(outputTriplets)
    
    return outputTriplets

# -------------------------------------------------------------------------------
# Fonction comparer les triplets extraits avec les triplets attendus
# -------------------------------------------------------------------------------
def compare_triplets(output_triplets, reference_triplets):
    # Comparison and error count
    errors = 0
    for i in range(len(output_triplets)):
        if output_triplets[i] != reference_triplets[i]:
            errors += 1
            print("--------------------")
            print(f"Erreur à la ligne {i+1}")
            print(f"Triplet extrait : {output_triplets[i]}")
            print(f"Triplet attendu : {reference_triplets[i]}")
            print("--------------------")

    # Calcul du taux de réussite
    success_rate = round((len(output_triplets) - errors) / len(output_triplets) * 100, 2)
    print("")
    print("++++++++++++++++++++++++++++++++++++++")
    print(f"Taux de réussite : {success_rate}% : {errors} erreurs sur {len(output_triplets)} lignes.")
    print("++++++++++++++++++++++++++++++++++++++")
    print("")

    # Graphique matplotlib pour visualiser les erreurs sous forme de pie
    import matplotlib.pyplot as plt
    labels = 'Erreurs', 'Réussites'
    sizes = [errors, len(output_triplets) - errors]
    colors = ['red', 'green']
    explode = (0.1, 0)  # explode 1st slice
    plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', shadow=True, startangle=140)
    plt.axis('equal')
    plt.show()  


    # Affichage d'un dataframe de comparaison des triplets
    pd.set_option('display.max_colwidth', None)

    df = pd.DataFrame({'id': [triplet.split(',')[0] for triplet in output_triplets],
                    #    'id': [triplet.split(',')[0] for triplet in reference_triplets],
                    'departure': [triplet.split(',')[1] if len(triplet.split(',')) > 1 else None for triplet in reference_triplets],
                    'departure predict': [triplet.split(',')[1] if len(triplet.split(',')) > 1 else None for triplet in output_triplets],
                    'destination': [triplet.split(',')[2] if len(triplet.split(',')) > 2 else None for triplet in reference_triplets],
                    'destination predict': [triplet.split(',')[2] if len(triplet.split(',')) > 2 else None for triplet in output_triplets]
                    }
                    )

    # On remplace les valeurs None par des chaînes vides
    df = df.fillna('')
    print("")
    print("---------------------------------------------------")
    print("Tableau récapitulatif : ")
    print(df)
    print("---------------------------------------------------")
    print("")

# -------------------------------------------------------------------------------
# Fonction pour prétraiter les triplets avant de les comparer : standardisation des caractères, correction des villes
# -------------------------------------------------------------------------------
def preprocess_triplets(triplets, fichier_villes = 'liste_villes_500.txt', verbose=True):

    # On convertit en majuscules et on remplace les caractères accentués, les apostrophes, les tirets et les underscores par des espaces
    preprocessed_triplets = [line.upper().replace('É', 'E').replace('È', 'E').replace('Ê', 'E').replace('À', 'A').replace('Ù', 'U').replace('Û', 'U').replace('Ô', 'O').replace('Î', 'I').replace('Ï', 'I').replace('Ë', 'E').replace('Ç', 'C').replace('\'', ' ').replace('-', ' ').replace('_', ' ') for line in triplets]

    with open(fichier_villes, 'r') as file:
    # Lire toutes les lignes du fichier dans une liste
        liste_villes = file.read().splitlines()

    # Récupère la meilleure correspondance pour chaque item de chaque triplet dans la liste de villes. S'il n'y a pas de correspondance, on met le triplet tel quel
    if verbose:
        print("triplet original : ")
        print(preprocessed_triplets)

    corrected_triplets = []  # Nouvelle liste pour stocker les triplets corrigés

    for triplet in preprocessed_triplets:
        triplet_split = triplet.split(',')
        # Recombine les éléments du triplet en une seule chaîne de caractères
        corrected_triplet = ','.join([difflib.get_close_matches(item, liste_villes, n=1, cutoff=0.8)[0] if difflib.get_close_matches(item, liste_villes, n=1, cutoff=0.8) else item for item in triplet_split])
        if verbose:
            print("triplet corrigé : " + corrected_triplet)
        corrected_triplets.append(corrected_triplet)

    preprocessed_triplets = corrected_triplets
    if verbose:
        print("triplets corrigés : ")
        print(preprocessed_triplets)
        print("____________________________________________")

    return preprocessed_triplets


# Créer une fonction qui retourne departure, destination
def departure_destination(text, nlp_lang, nlp_itineraire, fichier_villes = 'liste_villes_500.txt', verbose=False) :

    # Extraction des entités "DEPARTURE" et "DESTINATION" du texte
    itineraire = extract_departure_destination(text, nlp_lang, nlp_itineraire, verbose=verbose)
    if verbose:
        print("itineraire trouvé : ")
        print(itineraire)

    # Si on n'a pas trouvé les entités "DEPARTURE" ou "DESTINATION"
    if itineraire == "NOT_FRENCH" or itineraire == "NOT_TRIP":
        print("Pas d'itinéraire trouvé : " + itineraire)

    else:
        # Ajoute "1" au début de itineraire pour avoir le même format que les triplets
        itineraire = "1," + itineraire['departure'] + "," + itineraire['destination']


        # Prétraitement des triplets
        itineraire_traite = preprocess_triplets([itineraire], fichier_villes, verbose=verbose) # Attention : la fonction prend une liste en argument

        # On sépare les éléments du triplet
        itineraire_traite = itineraire_traite[0].split(',')

        return itineraire_traite[1], itineraire_traite[2] # On retourne l'élément 1 et 2 (départ et destination)