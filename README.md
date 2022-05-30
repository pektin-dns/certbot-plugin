# Pektin DNS Authenticator plugin for Certbot

Heavily inspired by the [certbot_dns_cloudflare](https://github.com/certbot/certbot/tree/master/certbot-dns-cloudflare) plugin.

## Usage

```sh
docker run --network pektin-compose_db -it --rm --name certbot \
    -v "/etc/letsencrypt:/etc/letsencrypt" \
    -v "/var/lib/letsencrypt:/var/lib/letsencrypt" \
    -v "$(pwd)/certbot-acme-client.pc3.ini:/certbot-acme-client.pc3.ini" \
    pektin/certbot certonly -a dns-pektin \
    -d 'pektin.club,*.pektin.club' \
    --agree-tos \
    --no-eff-email \
    -m pektin@y.gy \
    --dns-pektin-credentials /certbot-acme-client.pc3.ini
```

_certbot-acme-client-external.pc3.ini_

```ini
dns_pektin_username = acme-zyrr1ctqq3kgjw
dns_pektin_perimeter_auth = Basic QUpjS2poUzhYVFdybnl4elZSTFVFZ2NBLXRUX0lyYkRFLTJJejkwNTpfRHB2QW5URkMycWRLTGVHblJQMFhRVEJjUTJJLV9oOFBUcHpFRlZX
dns_pektin_confidant_password = c.4jvdBVkPML4JGrYfk7TOCjjL9ojEJb0WT5N4d7Qf2cMOvQTrMDcu9PrWYuLDyUoeGieEKyNGlFYmombJXnya4pxh709vN_uJ0PKuLiBPH6EXCJbe7DRgTZYLp9xoy5qdVeaoMw
dns_pektin_api_endpoint = http://api.pektin.club.localhost

```
