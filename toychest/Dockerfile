FROM node:10 as build-deps

# build react app in docker
COPY ./fsrc ./front
WORKDIR /front
RUN npm install
RUN npm run build

# prepare live environment

FROM python:3.6
LABEL MAINTAINER="WillDrug"

# Create app directory
WORKDIR /app
COPY --from=build-deps /front/build ./templates

# Install app dependencies
COPY ./requirements.txt ./

RUN pip install -r requirements.txt

# Bundle app source
COPY src ./

CMD [ "python", "toychest.py" ]