FROM python:3.8

COPY . /app
RUN mkdir /app/data
WORKDIR /app

RUN apt-get update && \
    apt-get install -y locales && \
    sed -i -e 's/# nb_NO.UTF-8 UTF-8/nb_NO.UTF-8 UTF-8/' /etc/locale.gen && \
    dpkg-reconfigure --frontend=noninteractive locales

ENV LANG nb_NO.UTF-8 UTF-8
ENV LC_ALL nb_NO.UTF-8 UTF-8

RUN pip install -r requirements.txt

RUN useradd -u 5050 -r appuser
USER appuser

ENTRYPOINT ["python", "main.py"]