#!/bin/bash

certbot certonly -w /var/www/certbot \
    --manual --manual-auth-hook /etc/letsencrypt/acme-dns-auth.sh --preferred-challenges dns \
    --debug-challenges --test-cert \
    --email $email \
    -d $domain \
    --agree-tos

