#!/bin/bash
source .env
#rm -rf data/certbot/conf/live/willdrug.me
docker-compose run --rm --env email --env domain --env main_domain --env DIGITALOCEAN_TOKEN --entrypoint "sh" certbot /etc/letsencrypt/first_run.sh

echo "### Reloading nginx ..."
docker-compose exec toynginx nginx -s reload
