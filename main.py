from Speech_Recognition.module.SpeechtoText import SpeechtoText
from NLP.module.EntityRecognitionService import EntityRecognitionService
from Path_Finding.module.FranceGraphBuilder import FranceGraphBuilder
from Path_Finding.module.GraphAlgorithms import GraphAlgorithms
import networkx as nx
import speech_recognition as sr

from codecarbon import OfflineEmissionsTracker

from constants import INPUT_READLINE, INPUT_FILE, INPUT_SPEECH, ERROR_NOT_TRIP, ERROR_NOT_FRENCH, ERROR_UNKNOWN
from utils import handle_input_type_selection, handle_input_type_csv, print_decorated, check_french

# Initialize services
SpeechtoText = SpeechtoText()
EntityRecognitionService = EntityRecognitionService()
FranceGraphBuilder = FranceGraphBuilder(
    city_data_file='Path_Finding/module/data/fr.csv', 
    graph_data_file='Path_Finding/module/data/fr.json'
)
GraphAlgorithms = GraphAlgorithms(FranceGraphBuilder.create_graph())
tracker = OfflineEmissionsTracker(
    country_iso_code="FRA",
    save_to_file=False,
    save_to_prometheus=True,
    log_level="critical"
)

def travel_order(id: str, departure: str, destination: str, debug = True) -> None:
    print(f"{id} - Itinéraire le plus court de {departure} à {destination}")
    
    if not GraphAlgorithms.check_node_exists(departure):
        print(f"{id} - Le noeud {departure} n'existe pas dans le graphe.")
        print(f"{id} - {ERROR_NOT_TRIP}")
        tracker.stop()
        exit()

    if not GraphAlgorithms.check_node_exists(destination):
        print(f"{id} - Le noeud {destination} n'existe pas dans le graphe.")
        print(f"{id} - {ERROR_NOT_TRIP}")
        tracker.stop()
        exit()

    # Find path
    path_dijkstra = GraphAlgorithms.dijkstra(departure, destination)
    path_a_star = GraphAlgorithms.astar_search(departure, destination)

    if debug:
        path_networkx = nx.shortest_path(GraphAlgorithms.graph, departure, destination, weight='weight')
        firsts_to_keep = 10
        all_paths = GraphAlgorithms.compute_all_paths(departure, destination, firsts_to_keep)

        print(f"Departure: {departure}")
        print(f"Destination: {destination}")

        print_decorated()

        print(f"Trajet Dijkstra: {path_dijkstra}")
        print(f"Trajet A*: {path_a_star}")
        print(f"Trajet NetworkX: {path_networkx}")

        print_decorated()

        print(f"Les {firsts_to_keep} plus courts trajets:")
        for path in all_paths:
            print(f"Trajet {path}: {all_paths[path]}")
    else:
        print(f"{id} - Trajet Dijkstra: {' -> '.join(path_dijkstra)}")
        print(f"{id} - Trajet A*: {' -> '.join(path_a_star)}")
        
    tracker.stop()

if __name__ == '__main__':
    tracker.start()
    # Choose input source: readline, csv or microphone
    print_decorated()
    input_type = handle_input_type_selection()
    id = 1

    if input_type == INPUT_READLINE:
        # Use readline as source
        text = input("Entrez votre texte: ")
        # Check if text is in French
        try:
            is_french = check_french(text)
        except Exception as e:
            print(f"{id} - {e.args[0]}")
            exit()
        # Extract locations from text
        departure, destination = EntityRecognitionService.extract_loc(text)
        travel_order(id, departure.capitalize(), destination.capitalize())
    elif input_type == INPUT_FILE:
        # Use csv as source
        filename = input("Entrez le nom du fichier csv: ")
        filepath = handle_input_type_csv(filename)
        # Read csv
        with open(filepath, 'r', encoding="utf-8", newline='') as f:
            for line in f:
                line_id, departure, destination = line.split(',')
                travel_order(line_id.strip(), departure.strip(), destination.strip())
    elif input_type == INPUT_SPEECH:
        # Use microphone as source
        audio = SpeechtoText.listen()
        try:
            # Save audio as text
            text = SpeechtoText.transcription(audio)
            # Extract locations from text
            departure, destination = EntityRecognitionService.extract_loc(text)
            travel_order(id, departure.capitalize(), destination.capitalize())
        except sr.UnknownValueError:
            print(f"{id} - {ERROR_UNKNOWN}")
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))
        except Exception as e:
            print(f"{id} - {e.args[0]}")
        finally:
            tracker.stop()