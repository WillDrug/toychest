#!/bin/bash

certbot certonly -w /var/www/certbot \
    --manual --manual-auth-hook /etc/letsencrypt/acme-dns-auth.sh --preferred-challenges dns \
    --debug-challenges \
    --email $email \
    -d $domain \
    --agree-tos

certbot certonly -w /var/www/certbot --domain $main_domain --agree-tos --preferred-challenges http
