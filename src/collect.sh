#!/bin/sh
while :
	do 	
		echo start
		python3 crosspost_monitor.py
		python3 repost_monitor.py
		echo 	succeed!
		sleep 300
done