FROM alpine
RUN apk add iptables
RUN echo "dr_sneaky" > /etc/hostname
COPY announce.sh /
RUN chmod +x /announce.sh
CMD sh -c "iptables -A INPUT -p icmp -j DROP; nc -lk -p 23 -e /announce.sh"
