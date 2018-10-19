FROM ruby:2.5

RUN apt update && apt -y install nodejs

ADD . /slate
WORKDIR /slate

RUN bundler install

CMD ["./deploy.sh", "--source-only"]

