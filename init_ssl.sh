#!/bin/bash
source .env
docker-compose run --rm --env email --env domain --entrypoint "sh" certbot /etc/letsencrypt/first_run.sh

echo "### Reloading nginx ..."
docker-compose exec toynginx nginx -s reload
