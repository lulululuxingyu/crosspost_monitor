#!/bin/sh
cr=0
re=0
echo "START HERE" >> ../output_data/information
echo "time: $(date +"%T")	num_crossposts: $cr" >> ../output_data/information
echo "time: $(date +"%T")	num_reposts: $re \n" >> ../output_data/information
while :
	do 	
		echo "#####" >> ../output_data/information

		#echo start collect crosspost events
		#cr=$(($cr + $(python3 crosspost_monitor.py)))
		#echo "time: $(date +"%T")	num_crossposts: $cr" >> ../output_data/information

		echo start collect repost events
		re=$(($re + $(python3 repost_monitor.py)))
		echo "time: $(date +"%T")	num_reposts: $re" >> ../output_data/information

		echo succeed!
		echo "#####\n" >> ../output_data/information
		sleep 500
done