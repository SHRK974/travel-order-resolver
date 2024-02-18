# T-AIA-901 - Travel Order Resolver

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Jupyter Notebook](https://img.shields.io/badge/jupyter-%23FA0F00.svg?style=for-the-badge&logo=jupyter&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2CA5E0?style=for-the-badge&logo=docker&logoColor=white)
![Prometheus](https://img.shields.io/badge/Prometheus-000000?style=for-the-badge&logo=prometheus&labelColor=000000)
![Grafana](https://img.shields.io/badge/Grafana-F2F4F9?style=for-the-badge&logo=grafana&logoColor=orange&labelColor=F2F4F9)

## Description

Build a program that processes **at least** text commands to issue an appropriate itinerary.

Your software will receive trip orders as text *(for instance an email)*, and potentially from voice *(for instance some phone recording)*, and will output at least one appropriate
travel line that fits the expectations of the customer.
It discriminates between valid and non-valid orders, and it identifies departure and destination

After text understanding, you may add an optimization process that finds the best path in a
distance graph, in order to get the optimal train connections

### Project Management

- [Trello](https://trello.com/b/JI3K2QoI/travel-order)

## Installation

### Docker

Using Docker, you can launch the project with a single command. Docker will download the necessary images and start the project.

It is composed of a Python CLI application and a resource monitoring interface for the application, available on port `9000` of your machine.

**Note the speech to text input, that uses the microphone, is not available in Docker.**

Install Docker and Docker Compose on your machine. Then run the following command in the project directory.

```bash
docker-compose up -d --build
```

### Local

To launch the project locally, you need to install Python dependencies and run the application.

**Note that the monitoring part of the project requires starting the Docker containers mentioned above.**

Install Python dependencies and download the necessary models for the NLP part.

```bash
pip install -r requirements.txt
```

```python
python -m spacy download fr_core_news_md
python -m spacy download fr_core_news_sm
```

## Usage

### Run in Docker

```bash
docker-compose run --rm -it travel-app
```

### Run locally

```bash
python main.py
```

3 modes are supported to input the trip order:

- Text input
- Voice input
- CSV input

#### Text input

You can input the trip order as text in the CLI. The program will process the text and output the best path.

#### Voice input

You can speak through the microphone and the program will process the voice input and output the best path.

#### CSV input

You can input the trip order as a CSV file. The program will process the CSV file and output the best path. The CSV file can handle mutliple trips at the same time and must be formatted as such: `ID,Departure,Destination`

Example:

```csv
1,Paris,Lyon
2,Lyon,Marseille
```

To use the CSV input, you first need to drop the CSV file in the `input` directory. Then you can use it in the CLI, by typing it's name. (without the `.csv` extension)

## Features

![Diagram](<resources/Service Diagram Travel Order.png>)

### NLP

The NLP part of the project is responsible for processing the input text and extracting the departure and destination of the trip. It is implemented using the [spaCy](https://spacy.io/) library. The library is used to process the input text and extract the entities from the text.

Moreover, the NLP is also used to detect the language of the input text. The language detection is implemented using the [langdetect](https://pypi.org/project/langdetect/) library.

Incorrect grammar and spelling mistakes are handled too.

### Pathfinder

The pathfinder part of the project is responsible for finding the best path in a distance graph, in order to get the optimal train connections. Two algorithms are implemented to find the best path, the Dijkstra algorithm and the A* algorithm.

All cities are not supported by the pathfinder as of now. You can find the supported cities in the graph in either `Path_Finding/a_star.py` or `Path_Finding/dijkstra.py`.

### Speech to Text

The speech to text part of the project is responsible for processing the voice input. It is implemented using the [SpeechRecognition](https://pypi.org/project/SpeechRecognition/) library. The library is used to process the voice input, turn it into text, and then process the text using the NLP part of the project.

#### Custom Implementation

A POC custom speech to text that does not use Google was implemented. It uses the [librosa](https://pypi.org/project/librosa/) library and the [hmmlearn](https://pypi.org/project/hmmlearn/) library to process a voice input and turn it into text.

## Security

Perform a vulnerability scan on the dependencies using [safety](https://pypi.org/project/safety/)

```bash
cat requirements.txt | docker run -i --rm pyupio/safety safety check --stdin
```

## Monitoring

The [codecarbon](https://codecarbon.io/) package is used to monitor the carbon footprint of the application. It pushes the data to a prometheus pushgateway. The data is then displayed in a Grafana dashboard.  

You can view the package methodolgy [here](https://mlco2.github.io/codecarbon/methodology.html#methodology).

## Documentation

The documentation of each module is available in their respective directories, in the `*.ipynb` files. The documentation is written in Jupyter Notebook format. It is intended to be used as a guide for the developers and the users of the project.
