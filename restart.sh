docker compose down
sleep 1
#rm -rf ./data
#mkdir ./data
docker image rm vpngate
sleep 1
docker compose up -d
sleep 2
docker ps --filter "name=vpngate" #--limit 1

