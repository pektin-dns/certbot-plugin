# Pektin DNS Authenticator plugin for Certbot

Heavily inspired by the [certbot_dns_cloudflare](https://github.com/certbot/certbot/tree/master/certbot-dns-cloudflare) plugin.

## Usage

```sh
certbot certonly --test-cert -a dns-pektin -d 'pektin.xyz,\*.pektin.xyz' --dns-pektin-credentials dns-pektin.ini --dns-pektin-propagation-seconds 60
```

_dns-pektin.ini_

```ini
dns_pektin_username = ui-9_saFU5eDwiHig
dns_pektin_password = 1bUvDccqLmCSvYrC3IrBfJftI7mksTyPAKqRw97tpvCJkJzCt58aplwExPPMLU8QZbRLYRIr8sxFq78gGTy3-z_MJce9vxuWdh6wR19z-YHFZyMs61yk7HYNp1yToHTTpxqMUA
dns_pektin_vaultEndpoint = http://65.108.88.212:8200
```

**TODO**
