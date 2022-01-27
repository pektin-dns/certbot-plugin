# Pektin DNS Authenticator plugin for Certbot

Heavily inspired by the [certbot_dns_cloudflare](https://github.com/certbot/certbot/tree/master/certbot-dns-cloudflare) plugin.

## Usage

```sh
certbot certonly --test-cert -a dns-pektin -d 'pektin.xyz,\*.pektin.xyz' --dns-pektin-credentials certbot-acme-client-connection-config.ini --dns-pektin-propagation-seconds 60
```

_certbot-acme-client-connection-config.ini_

```ini
username = acme-j7yK6wle6g9ocw
confidantPassword = c.r_0EwSGjobc4t2shWtxUCP43IlpKyYDiNa54AjLdj9Ei9UcypLxHggi_U0y8MvxRu5PnJhncrmujljNDsLG6zacaY5P3K95Li5SBXRZ-HsF14niqGfLnia9R2A_v_URe2smUEQ
pektinApiEndpoint = http://127.0.0.1:3001
```

**TODO**

`cd ../certbot-test && ./test-certbot.sh && cd -`
