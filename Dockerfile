FROM ubuntu:22.04
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Tokyo
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
#FROM alpine:latest

#RUN set -eux; \
#    apk add --no-cache python3 iputils-ping iproute2 wget

#WORKDIR /tmp
#RUN wget http://dl-cdn.alpinelinux.org/alpine/v3.19/community/x86_64/libnm-1.44.4-r0.apk
#RUN wget http://dl-cdn.alpinelinux.org/alpine/v3.19/community/x86_64/networkmanager-1.44.4-r0.apk
#RUN wget http://dl-cdn.alpinelinux.org/alpine/v3.19/community/x86_64/networkmanager-cli-1.44.4-r0.apk
#RUN wget http://dl-cdn.alpinelinux.org/alpine/v3.19/community/x86_64/networkmanager-common-1.44.4-r0.apk
#RUN wget http://dl-cdn.alpinelinux.org/alpine/v3.19/community/x86_64/networkmanager-openvpn-1.10.2-r1.apk
#RUN apk add /tmp/networkmanager-1.44.4-r0.apk /tmp/networkmanager-cli-1.44.4-r0.apk /tmp/networkmanager-common-1.44.4-r0.apk /tmp/libnm-1.44.4-r0.apk 

#RUN apk add openvpn networkmanager-openvpn

#RUN apk add /tmp/networkmanager-openvpn-1.10.2-r1.apk

RUN    apt-get update && apt-get install -y network-manager-openvpn network-manager-openvpn-gnome python3 iputils-ping iproute2 pip
#RUN    systemctl mask NetworkManager.service.

COPY index.py /usr/src/app/index.py
COPY docker-entrypoint.sh /docker-entrypoint.sh 
COPY headers.json /usr/src/app/headers.json
COPY urltest.txt /usr/src/app/urltest.txt
COPY vpn-resolver.conf /usr/src/app/vpn-resolver.conf

RUN chmod +x /docker-entrypoint.sh

WORKDIR /usr/src/app/

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

RUN apt-get install -y dante-server curl && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY dante.conf /etc/danted.conf

EXPOSE 8282

#RUN systemctl restart NetworkManager

ENTRYPOINT ["/docker-entrypoint.sh"]
