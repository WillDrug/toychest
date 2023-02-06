#!/bin/bash

docker-compose run --rm -e email="$email" -e domain_main="$domain_main" -e domain_wild="$domain_wild" --entrypoint "\
  certbot certonly -w /var/www/certbot \
    --manual --manual-auth-hook /etc/letsencrypt/acme-dns-auth.py --preferred-challenges dns \
    --email \$email \
    -d \$domain_main \
    -d \$domain_wild \
    --agree-tos" certbot
echo

echo "### Reloading nginx ..."
docker-compose exec toynginx nginx -s reload
