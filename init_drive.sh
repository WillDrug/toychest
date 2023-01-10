# run with user, password, secret for an auth flow.
# expecting hostname to be valid for a callback url, though.
# can use -e drive_host=127.0.0.1
# $4 -> {'config_file_id': '....'} folder id
docker run --rm -ti --network toychest_toysupport -e username=$1 -e password=$2 -e init_drive=true -p 8080:8080 --entrypoint python -e drive_secret=$3 toydiscover:1.0.0 modify_config.py --config_json $4
docker restart toydiscover