FROM python:3.9

WORKDIR /auth

RUN  apt-get update && apt-get install -y
RUN  pip3 install pipenv
RUN  pipenv install
COPY Pipfile Pipfile.lock /auth/

COPY . /auth

EXPOSE 8081

CMD ["sh", "launcher.sh"]