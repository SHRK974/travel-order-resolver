FROM python:3.11.7

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libportaudio2 \
    libportaudiocpp0 \
    portaudio19-dev \
    libasound-dev \
    libsndfile1-dev

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt
RUN python -m spacy download fr_core_news_md
RUN python -m spacy download fr_core_news_lg

COPY . .

ENV AUDIO_DISABLED=1

CMD ["python", "main.py"]