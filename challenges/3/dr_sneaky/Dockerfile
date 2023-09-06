FROM alpine
COPY announce.sh /
RUN chmod +x /announce.sh
CMD sh -c "nc -lk -p 23 -e /announce.sh"
