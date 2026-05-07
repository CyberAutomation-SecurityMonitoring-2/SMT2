# SMT2
Automated SOC monitoring solution for Catnip Games International — CMP-L022-0 Security Monitoring Team 2
SO WE MADE A ROUGH DOCUMENTATION OF ALL KEY ASPECTS LIKE IP's, CMDS THOUGH NOT EVERYTHING JUST FEW:

config - nat adapter
name - so-nat
ip default - 10.0.2.0/24 (
mgmt. ip - 10.0.2.10 ( security onion)
gateway - 10.0.2.6
(workstation)desktop 10.0.2.1


so-admin
so-team
sudo ip addr add 192.168.1.1/24 dev bond0
sudo ip link set bond0 up

suricata alerts
sudo cat daily_report.md
cat incidents.log
python3 overallreport.py




Ubuntu Server
Login - student
PW - Student1

game server
login - gameadmin
pw - so-team


network configs
SO - 192.168.1.1 & 10.0.2.10
game server - 192.168.1.10
attacker - 192.168.1.20
user simulation - 192.168.1.30
casual user - 192.168.1.40
monitoring  - 192.168.1.50

Commands 
sudo apt update
sudo apt install python3-pip -y
pip3 install flask
python3 game_server.py
curl http://<server-ip>:5000/health

sudo apt update
sudo apt install python3-pip -y
pip3 install requests
python3 attacker.py


import json
from datetime import datetime
