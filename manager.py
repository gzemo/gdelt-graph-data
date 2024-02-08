import os
import pandas as pd
import datetime as dt
from run_day import run_single_day

def last_progress():
	return str(sorted([int(item.split("_")[0]) for item in os.listdir("./networks") if item!="rawdata"])[-1] + 1)

def days_left(last):
	tmstamp = pd.date_range(pd.Timestamp(last), pd.Timestamp(dt.datetime.today())).tolist()

	tmp = []
	for item in tmstamp:
		year = str(item.date().year)
		month = "0"+str(item.date().month) if len(str(item.date().month))==1 else str(item.date().month) 
		day = "0"+str(item.date().day) if len(str(item.date().day))==1 else str(item.date().day)
		tmp.append(f"{year}{month}{day}")
	return tmp

if __name__ == "__main__":

	for day in days_left(last_progress()):
		print("Performing:", day)
		run_single_day(day)
