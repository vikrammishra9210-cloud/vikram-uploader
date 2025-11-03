FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update             && apt-get install -y --no-install-recommends                gcc                libffi-dev                ffmpeg                aria2                wget                build-essential             && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# copy requirements first for better cache
COPY requirements.txt /app/requirements.txt
RUN pip3 install --no-cache-dir -r /app/requirements.txt

# copy app
COPY . /app

# expose optional port (not required for bots)
EXPOSE 8000

CMD ["python3", "main.py"]
ENV PYROGRAM_NO_APP_ENV=1
