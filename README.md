# crosspost_monitor
	# crosspost:
		- script: src/crosspost_monitor.py
		- input: input_data/account_list
		- output: output_data/crosspost_data.tsv
		- stability:
			successfully collected 40 submissions(5 minute interval)

			TODO:
				test three accounts with 50 crossposts each
	# repost:
		- script: src/repost_monitor.py
		- input: input_data/spreadsheet_ids
		- output: output_data/crosspost_data.tsv
		- stability:
			successfully collected 100 submissions(5 minute interval)

	# challenge:
		- what's the rate of generation of events? every 10 minutes
		- what's the number of accounts and number of spread sheets
		- figure out the capacity of the script