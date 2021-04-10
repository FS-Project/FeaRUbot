# INFO : This is a copy of the source code from the MoveAngel repo, and has the permission of the owner.
#

FROM ferubot/docker:alpine-latest

RUN mkdir /FeaRUbot && chmod 777 /FeaRUbot
ENV PATH="/FeaRUbot/bin:$PATH"
WORKDIR /FeaRUbot

RUN git clone https://github.com/FS-Project/FeaRUbot -b main /FeaRUbot

#
# Copies session and config(if it exists)
#
COPY ./sample_config.env ./fearubot.session* ./config.env* /FeaRUbot/

#
# Make open port TCP
#
EXPOSE 80 443

#
# Finalization
#
CMD ["python3","-m","fearubot"]
