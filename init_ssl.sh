#!/bin/bash

docker-compose run --rm --entrypoint "\
  certbot certonly --webroot -w /var/www/certbot \
    --manual --manual-auth-hook /etc/letsencrypt/acme-dns-auth.py --preferred-challenges dns
    --email $email \
    -d $domain_main \
    -d $domain_wild \
    --rsa-key-size $rsa_key_size \
    --agree-tos \
    --force-renewal" certbot
echo

echo "### Reloading nginx ..."
docker-compose exec toynginx nginx -s reload