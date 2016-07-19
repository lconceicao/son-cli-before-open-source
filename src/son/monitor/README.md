# son-monitor

Monitor metrics of a deployed service (from the SONATA SDK emulator or Service Platform).
Generate and/or export metrics that are useful for debugging and analyzing the service performance.

Below figure shows the architecture of the son-monitor tools inside the total SONATA SDK:
- A set of monitoring functions implemented in son-emu
- External docker containers to gather and store metrics (cAdvisor, Prometheus)
- Metric install and retrieval functions inside son-cli

![son-monitor](../../../figures/Son-monitor-architecturev2.png)


```
usage: son-monitor [-h]
                   [--containers [{all,no-son-emu} [{all,no-son-emu} ...]]]
                   [--vim VIM] [--vnf_name VNF_NAME] [--datacenter DATACENTER]
                   [--image IMAGE] [--dcmd DOCKER_COMMAND] [--net NETWORK]
                   [--query QUERY] [--input INPUT] [--output OUTPUT]
                   [--source SOURCE] [--destination DESTINATION]
                   [--weight WEIGHT] [--match MATCH] [--bidirectional]
                   [--metric METRIC] [--cookie COOKIE]

                   {init,profile,query,interface,flow_mon,flow_entry,flow_total}
                   [{start,stop}]

    Install monitor features on or get monitor data from the SONATA platform/emulator.


positional arguments:
  {init,profile,query,interface,flow_mon,flow_entry,flow_total}
                        Monitoring feature to be executed
  {start,stop}          Action for interface or flow metric:
                                  flow_mon : export the metric
                                  flow_entry : (un)set the flow entry
                                  flow_total : flow_entry + flow_mon
                                  Action for init:
                                  start: setup the requested containers
                                  stop: stop the requested containers


optional arguments:
  -h, --help            show this help message and exit
  --containers [{all,no-son-emu} [{all,no-son-emu} ...]], -cn [{all,no-son-emu} [{all,no-son-emu} ...]]
                        Containers for for init:
                                  all: cAdvisor, Prometheus DB + Pushgateway, son-emu (with default topology)
                                  no-son-emu: all the above except son-emu

  --vim VIM, -v VIM     VIM where the command shold be executed (emu/sp)
  --vnf_name VNF_NAME, -vnf VNF_NAME
                        vnf name:interface to be monitored
  --datacenter DATACENTER, -d DATACENTER
                        Data center where the vnf is deployed
  --image IMAGE, -i IMAGE
                        Name of container image to be used e.g. 'ubuntu:trusty'
  --dcmd DOCKER_COMMAND, -cmd DOCKER_COMMAND
                        Startup command of the container e.g. './start.sh'
  --net NETWORK         Network properties of a compute instance e.g.           '(id=input,ip=10.0.10.3/24),(id=output,ip=10.0.10.4/24)' for multiple interfaces.
  --query QUERY, -q QUERY
                        prometheus query
  --input INPUT, -in INPUT
                        input interface of the vnf to profile
  --output OUTPUT, -out OUTPUT
                        output interface of the vnf to profile
  --source SOURCE, -src SOURCE
                        vnf name:interface of the source of the chain
  --destination DESTINATION, -dst DESTINATION
                        vnf name:interface of the destination of the chain
  --weight WEIGHT, -w WEIGHT
                        weight edge attribute to calculate the path
  --match MATCH, -ma MATCH
                        string holding extra matches for the flow entries
  --bidirectional, -b   add/remove the flow entries from src to dst and back
  --metric METRIC, -me METRIC
                        tx_bytes, rx_bytes, tx_packets, rx_packets
  --cookie COOKIE, -c COOKIE
                        flow cookie to monitor
```

This command starts all the related docker files (cAdvisor, Prometheus DB, PushGateway and son-emu (experimental))
```
son-monitor init
```

After a service has been deployed on the SDK emulator (son-emu), son-monitor can be used.
Son-monitor uses the son-emu rest api and Prometheus.

*Example1*: Expose the tx_packets metric from son-emu network switch-port where vnf1 (default 1st interface) is connected.
The metric is exposed to the Prometheus DB.
```
son-monitor son-monitor interface start -vnf vnf1 -me tx_packets
```

*Example2*: Install a flow_entry in son-emu, monitor the tx_bytes on that flow_entry.
The metric is exposed to the Prometheus DB.
```
son-monitor flow_total start -src vnf1  -dst vnf2  -ma "dl_type=0x0800,nw_proto=17,udp_dst=5001"  -b -c 11 -me tx_bytes
```

*Example3*:  Send a query to the prometheus DB to retrieve the earlier exposed metrics, or default metric exposed by cAdvisor.
The Prometheus query language can be used.
```
son-monitor query --vim emu -d datacenter1 -vnf vnf1 -q 'sum(rate(container_cpu_usage_seconds_total{id="/docker/<uuid>"}[10s]))'
```
