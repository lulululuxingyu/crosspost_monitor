#!/bin/sh
cr=0
cro=0
re=0
rep=0
set -e
echo "START HERE" >> ../output_data/information
echo "time: $(date +"%T")	num_crossposts: $cr" >> ../output_data/information
echo "time: $(date +"%T")	num_reposts: $re \n" >> ../output_data/information
while :
	do 	
		echo "#####" >> ../output_data/information

		echo start collect crosspost events
		#(cr=$(($cr + $(python3 crosspost_monitor.py)))) || true
		cro=$(python3 crosspost_monitor.py) || true
		cr=$((cro + cr))
		echo "time: $(date +"%T")	num_crossposts: $cr" >> ../output_data/information
		echo "crosspost count: $cr"

		echo start collect repost events
		#(re=$(($re + $(python3 repost_monitor.py)))) || true
		rep=$(python3 repost_monitor.py) || true
		re=$((rep + re))
		echo "time: $(date +"%T")	num_reposts: $re" >> ../output_data/information
		echo "repost count: $re"

		echo succeed!
		echo "#####\n" >> ../output_data/information
		sleep 500
done
