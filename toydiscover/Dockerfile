FROM python:3.6

LABEL MAINTAINER="WillDrug"

# Create app directory
WORKDIR /app

# Install app dependencies
COPY ./requirements.txt ./

RUN pip install -r requirements.txt

# Bundle app source
COPY toydiscover.py ./

CMD [ "python", "toydiscover.py" ]