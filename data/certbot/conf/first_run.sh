#!/bin/bash

# no digitalocean acme auth hook
#certbot certonly -w /var/www/certbot \
#    --manual --manual-auth-hook /etc/letsencrypt/acme-dns-auth.sh --preferred-challenges dns \
#    --debug-challenges \
#    --email $email \
#    -d $domain \
#    --agree-tos

#certbot certonly -w /var/www/certbot --domain $main_domain --agree-tos --preferred-challenges http


# digital ocean token usage
echo "dns_digitalocean_token = $DIGITALOCEAN_TOKEN" > creds.ini
chmod go-rwx creds.ini
sudo certbot certonly -w /var/www/certbot --dns-digitalocean --dns-digitalocean-credentials creds.ini -d $main_domain -d $domain