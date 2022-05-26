docker build . -t pektin/certbot
docker run --network pektin-compose_db -it --rm --name certbot \
    -v "/etc/letsencrypt:/etc/letsencrypt" \
    -v "/var/lib/letsencrypt:/var/lib/letsencrypt" \
    -v "/root/pektin-compose/secrets/certbot-acme-client.pc3.ini:/certbot-acme-client.pc3.ini" \
    pektin/certbot certonly -a dns-pektin -d 'pektin.club,*.pektin.club' --dns-pektin-credentials /certbot-acme-client.pc3.ini 