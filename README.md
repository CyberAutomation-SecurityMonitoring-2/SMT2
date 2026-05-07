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
------------------------------------------------------------------------------------------------------------


HERE IS THE ACTUAL TROUBLESHOOT WE WENT TROUGH AND THE IT'S DETAILS:
Use this version for:

```bash
nano ~/SecurityMonitoring-Team2/docs/troubleshooting_guide.md
```

Then paste the content below.

````md
# Troubleshooting Guide

## Security Monitoring Team 2  
## Security Onion, VM Networking, Elasticsearch and Kibana

This troubleshooting guide documents the main technical issues encountered during the Security Monitoring project and the steps taken to resolve them. The guide is written to support future reproduction of the lab environment and to provide a clear operational record of how faults were identified, investigated, and fixed.

The main areas covered are:

- Virtual machine network connectivity
- Security Onion monitoring interface configuration
- Elasticsearch and Kibana log visibility
- Zeek and Suricata data ingestion
- PCAP visibility
- Traffic generation issues
- End-to-end validation of the monitoring pipeline

---

## 1. VM Communication Failure

### Problem

During the initial setup, the attacker VM was unable to communicate with the target server. Ping tests failed, and no traffic was visible in Security Onion. This blocked the rest of the monitoring workflow because Suricata, Zeek, Elasticsearch and Kibana all depended on live network traffic being generated and captured correctly.

### Investigation

The first step was to confirm whether the issue was caused by the operating systems, the IP configuration, or the virtual network setup. I checked the IP addresses and active interfaces on each VM using:

```bash
ip a
````

I then tested basic connectivity using:

```bash
ping 192.168.1.10
```

The test showed that the attacker VM and target server were not able to reach each other.

### Root Cause

The attacker VM and target server were using different virtual network modes. The attacker VM was configured with a NAT adapter, while the target server was connected to a Host-only/Internal network. This meant the machines were not on the same Layer 2 network segment, so traffic could not pass between them.

### Resolution

I reconfigured the virtual machines so that all systems used the same Host-only/Internal network. Static IP addresses were then assigned to keep the environment stable:

| Machine        |     IP Address | Purpose                                  |
| -------------- | -------------: | ---------------------------------------- |
| Target Server  | `192.168.1.10` | Simulated victim service                 |
| Attacker VM    | `192.168.1.20` | Traffic generation and attack simulation |
| Security Onion |  `192.168.1.1` | Monitoring and analysis platform         |

After applying the changes, I repeated the ping test:

```bash
ping 192.168.1.10
```

### Outcome

Connectivity between the attacker VM and target server was restored. This allowed test traffic to be generated and gave Security Onion the opportunity to capture live network activity.

### Lesson Learned

Before troubleshooting SIEM dashboards or IDS rules, the network layer must be confirmed first. If the VMs cannot communicate, the monitoring tools will not receive any useful data.

---

## 2. Security Onion Monitoring Interface Issue

### Problem

After VM connectivity was restored, Security Onion was still not showing the expected traffic. The system was running, but packets were not being captured properly.

### Investigation

I checked the network interfaces on Security Onion using:

```bash
ip a
```

The aim was to identify which interface was being used for management and which interface was intended for monitoring. Security Onion requires the monitoring interface to be connected to the same network segment as the systems being observed.

### Root Cause

The monitoring interface was not correctly aligned with the traffic-generating network. Security Onion was not listening on the interface connected to the Host-only/Internal segment used by the attacker VM and target server.

### Resolution

I reviewed the Security Onion interface configuration and confirmed the correct adapter for packet capture. The monitoring interface was then placed on the same virtual network as the attacker and target machines.

After making the correction, I generated new traffic and checked whether Security Onion was able to observe it.

### Outcome

Security Onion started capturing traffic from the lab network. This confirmed that the monitoring interface was now correctly positioned.

### Lesson Learned

Security Onion must have a clear separation between its management interface and monitoring interface. The management interface is used to access the platform, while the monitoring interface must be connected to the network where the traffic is taking place.

---

## 3. Kibana Dashboards Showing No Data

### Problem

Kibana dashboards were empty even though the lab environment was generating traffic. This created a major issue because the team needed Kibana to demonstrate Suricata alerts, Zeek logs and security event analysis.

### Investigation

I approached the issue by checking the pipeline in stages:

1. Confirm that traffic was being generated.
2. Confirm that Security Onion could capture the traffic.
3. Confirm that Zeek and Suricata were producing logs.
4. Confirm that logs were being shipped into Elasticsearch.
5. Confirm that Kibana was querying the correct data and time range.

This avoided guessing and helped isolate the fault.

### Root Cause

The issue was not with Kibana itself. Zeek and Suricata were producing logs, but the data was not appearing correctly in Elasticsearch/Kibana. The ingestion path and log shipping configuration needed to be checked and corrected.

### Resolution

I verified the log source locations and checked the ingestion configuration. After correcting the relevant path/configuration issue, I restarted the log shipping service:

```bash
sudo systemctl restart filebeat
```

I then returned to Kibana and refreshed the dashboard/index view.

Useful checks included:

```bash
sudo systemctl status filebeat
```

```bash
sudo systemctl status elasticsearch
```

### Outcome

Suricata and Zeek data started appearing in Kibana. This confirmed that the ingestion pipeline was working and that the issue had been caused by log shipping rather than a dashboard fault.

### Lesson Learned

An empty Kibana dashboard does not always mean that detection has failed. The problem may be in log collection, ingestion, indexing, time filters or query syntax. Each stage of the pipeline should be tested separately.

---

## 4. Elasticsearch Ingestion and Index Visibility

### Problem

Some logs were being generated but were not immediately visible in Elasticsearch or Kibana. This made it difficult to confirm whether alerts were being correctly processed.

### Investigation

I checked whether Elasticsearch was receiving the expected data and whether the correct fields were available for searching. I also reviewed whether the correct dataset names were being used inside Kibana queries.

Example KQL checks included:

```kql
event.dataset: suricata.alert
```

```kql
event.dataset: zeek.http
```

### Root Cause

The issue was linked to a combination of ingestion visibility and query alignment. In some cases, the data existed but the dashboard or search query was not using the correct dataset field or time range.

### Resolution

I corrected the filters and confirmed that the dashboards were using the appropriate fields. The following queries were used to validate Suricata and Zeek visibility:

```kql
event.dataset: suricata.alert AND source.ip: 192.168.1.20
```

```kql
event.dataset: zeek.http AND url.path: "/login"
```

For failed login analysis, I used:

```kql
event.dataset: zeek.http AND url.path: "/login" AND http.status_code: 401
```

### Outcome

The relevant Suricata and Zeek records became visible in Kibana. The dashboards could then be used to analyse attacker traffic, HTTP requests and failed login activity.

### Lesson Learned

Kibana queries must match the actual indexed field names. A small mismatch in field names, dataset values or time filters can make valid data appear missing.

---

## 5. PCAP Data Not Visible

### Problem

PCAP evidence was expected to be available, but initially the captures were not visible through the Security Onion interface.

### Investigation

I confirmed that traffic was being generated and that Security Onion had already started capturing packets. I then checked the time filter in the interface because PCAP visibility is often affected by the selected time window.

### Root Cause

The selected dashboard time range was too narrow. The interface was only showing recent data, while the relevant traffic had been generated outside that window.

### Resolution

I expanded the time range from the default short window to a wider range, such as the last 24 hours. I then regenerated traffic from the attacker VM to ensure new PCAP entries were available.

### Outcome

PCAP data became visible and could be used to support investigation and validation.

### Lesson Learned

When evidence appears missing, always check the time range before assuming that capture has failed. In SOC tools, time filters are a common reason for apparently empty results.

---

## 6. Missing curl on the Attacker VM

### Problem

The attacker VM did not have `curl` installed, which affected the original plan for generating HTTP test traffic against the target server.

### Investigation

The issue was confirmed when the expected `curl` command failed. Installing new tools was possible, but it was not the most efficient option because Python was already available on the VM.

### Root Cause

The VM image did not include `curl` by default.

### Resolution

Instead of installing additional packages, I used Python’s built-in `urllib` module to generate HTTP requests:

```bash
python3 -c "import urllib.request; urllib.request.urlopen('http://192.168.1.10:5000/login')"
```

This allowed HTTP traffic to be generated without changing the system package state.

### Outcome

HTTP requests were successfully generated from the attacker VM to the target server. Zeek recorded the HTTP activity and the traffic became available for dashboard analysis.

### Lesson Learned

In a restricted or minimal Linux environment, built-in tools can often replace missing utilities. Python is especially useful for quick traffic generation and testing.

---

## 7. Kibana Filters Returning Empty Results

### Problem

Some Kibana filters returned no results even when traffic had been generated successfully.

### Investigation

I checked three areas:

1. Whether the traffic had actually been generated.
2. Whether the selected time range included the traffic.
3. Whether the KQL fields matched the indexed data.

### Root Cause

The issue was caused by filter and time-range mismatches rather than a complete pipeline failure. In some cases, the filter was too narrow or did not match the available field values.

### Resolution

I tested broader filters first and then narrowed them down.

Broad Suricata check:

```kql
event.dataset: suricata.alert
```

Broad Zeek HTTP check:

```kql
event.dataset: zeek.http
```

Attacker-specific Suricata check:

```kql
event.dataset: suricata.alert AND source.ip: 192.168.1.20
```

Login-specific Zeek check:

```kql
event.dataset: zeek.http AND url.path: "/login"
```

Failed login check:

```kql
event.dataset: zeek.http AND url.path: "/login" AND http.status_code: 401
```

### Outcome

The correct filters were identified and saved for use in the dashboards.

### Lesson Learned

Start with broad searches and narrow down gradually. This makes it easier to separate a real data issue from a query issue.

---

## 8. End-to-End Pipeline Validation

### Problem

After resolving the individual faults, the full monitoring pipeline needed to be tested to confirm that the project environment worked as one system.

The required flow was:

```text
Attacker VM traffic
        ↓
Target Server
        ↓
Security Onion capture
        ↓
Suricata alert / Zeek log
        ↓
Elasticsearch ingestion
        ↓
Kibana dashboard visibility
        ↓
PCAP and event correlation
```

### Investigation

I generated controlled HTTP traffic from the attacker VM and checked each stage of the pipeline. The goal was not only to confirm that data appeared in Kibana, but also to confirm that the same session could be traced across multiple sources.

### Resolution

I generated test traffic from the attacker VM:

```bash
python3 -c "import urllib.request; urllib.request.urlopen('http://192.168.1.10:5000/login')"
```

I then checked for related Suricata and Zeek records in Kibana using:

```kql
source.ip: 192.168.1.20
```

I also used `community_id` where available to correlate the same session across Suricata alerts, Zeek logs and PCAP evidence.

### Outcome

The full pipeline was successfully validated. Traffic generated from the attacker VM was captured by Security Onion, processed by Zeek and Suricata, ingested into Elasticsearch and displayed in Kibana.

### Lesson Learned

A SOC monitoring setup should never be considered complete just because individual services are running. The full chain must be tested from traffic generation to dashboard visibility.

---

## 9. Summary of Issues and Fixes

| Issue                              | Root Cause                                 | Fix Applied                                         | Result                            |
| ---------------------------------- | ------------------------------------------ | --------------------------------------------------- | --------------------------------- |
| VMs could not communicate          | Different virtual network modes            | Reconfigured all VMs to Host-only/Internal          | Connectivity restored             |
| Security Onion captured no traffic | Wrong monitoring interface/network segment | Corrected monitoring interface placement            | Packet capture worked             |
| Kibana showed no logs              | Log shipping/ingestion issue               | Corrected path/configuration and restarted Filebeat | Logs appeared in Kibana           |
| PCAP not visible                   | Time filter too narrow                     | Expanded time range and regenerated traffic         | PCAP entries visible              |
| curl missing                       | Tool not installed on attacker VM          | Used Python `urllib` instead                        | HTTP traffic generated            |
| Filters returned no results        | Query/time-range mismatch                  | Tested broad filters before narrow KQL              | Correct dashboard filters created |
| Correlation needed across tools    | Events had to be linked manually           | Used `community_id` where available                 | Suricata, Zeek and PCAP linked    |

---

## 10. Final Notes

The main lesson from this troubleshooting process is that Security Onion depends on a complete and correctly connected pipeline. A fault at any layer can make the whole system appear broken.

The most effective approach was to troubleshoot in order:

1. Confirm VM network connectivity.
2. Confirm Security Onion can see the traffic.
3. Confirm Zeek and Suricata are producing logs.
4. Confirm logs are being ingested into Elasticsearch.
5. Confirm Kibana is using the correct index, query and time range.
6. Confirm PCAP evidence is available.
7. Validate the full process end to end.

This approach avoided unnecessary reinstallations and helped identify the actual root causes. It also produced a repeatable troubleshooting method that can be used by future team members or assessors reviewing the project.

```
