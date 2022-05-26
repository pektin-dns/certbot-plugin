FROM certbot/certbot
COPY ./ ./certbot_dns_pektin
RUN pip install -e ./certbot_dns_pektin