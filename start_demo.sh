pkill python
cd ~/ivs
pkill chrome
python hub.py &
python ivs.py @Configs/hub.ini &
python ivs.py @Configs/country1.ini &
python ivs.py @Configs/country2.ini &
python ivs.py @Configs/country3.ini &
python ivs.py @Configs/country4.ini &
#nohup python ivs.py @child.ini &
sleep 10
google-chrome http://127.0.0.1:8001 http://127.0.0.1:8001/log http://localhost:8002/demo/verify http://localhost:15672/#/exchanges/%2F/OBTB http://127.0.0.1:8002/demo/upload &
while true; do
    sleep 100
done
