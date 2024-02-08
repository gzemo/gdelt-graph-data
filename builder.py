import os
import io
import zipfile
import requests
import numpy as np
import pandas as pd


class DayEstimator():

	def __init__(self, date, filepath_country_codes):
		assert isinstance(date, str) and len(date)==8, "Not a valid input date!"
		country_codes = pd.read_csv(filepath_country_codes, sep="\t")
		country_list = country_codes[country_codes.Alpha3_code.notnull()].Alpha3_code.tolist()
		self.date = date
		self.country_list = country_list
		self.record_list = []
		self.theta1 = 0.025
		self.theta2 = 0.01
		self.theta3 = 0.01
		self.matrix = None
		self.pattern = "|".join(self.country_list).replace(" ","")
		
	def _initialize_adiacency_matrix(self):
		self.matrix = np.zeros((len(self.country_list), len(self.country_list)))

	def _retrieve_daily_records(self):
		#self.record_list = self.masterfile[self.masterfile[0]==int(self.date)][1].array.tolist()

		prefix = "http://data.gdeltproject.org/gdeltv2"
		self.record_list = [ f"{prefix}/{self.date}{'0'+str(hour) if len(str(hour))==1 else str(hour)}{timestamp}00.export.CSV.zip"\
							for hour in range(0,23+1)\
							for timestamp in ["00", "15", "30", "45"] ]

	def _download_process_single(self, single_record_url, clean_after_computation=True):
		"""
		Single timestamp (15min records) download, extraction, filtering and processing
		to have the current 15min graph 
		Args:
			single_record_url: (str) url for that given endpoint
			clean_after_computation: (bool) whether to delete the 15min timestamp csv after
				computations
		"""
		single_record_url = single_record_url.strip()
		tmp = single_record_url.split("/")[-1].lower().split(".")
		date, spec = tmp[0], tmp[1]

		print(f"  Downloading: {date[0:4]}/{date[4:6]}/{date[6:8]} - {date[8:10]}:{date[10:12]} {spec}", end="  ")
		
		# performing request and check integrity
		r = requests.get(single_record_url)
		if not r.ok:
			print(f"*** Warning: no valid response gathered! date: {date} ; spec: {spec}")
			return 

		# zip extraction 
		z = zipfile.ZipFile(io.BytesIO(r.content))
		z.extractall(f"./rawdata/")
		
		# address the empty file condition
		try:
			current = pd.read_csv(f"./rawdata/{date}.{spec}.CSV", sep="\t", header=None)
		except Exception:
			print(f"*** Warning: something wrong in the process of reading the current file! date: {date} ; spec: {spec}")
			return 

		current = current[(current[5].notnull()) & (current[15].notnull())]
		current_filtered = current[(current[5].str.fullmatch(self.pattern)) &\
			(current[15].str.fullmatch(self.pattern))]

		n_records = current_filtered.shape[0]
		print(f"Found: {n_records}{' '*2 if len(str(n_records))<3 else ' '}valid events: now parsing records...")
		
		for i in range(current_filtered.shape[0]):

			current_row = current_filtered.iloc[i]

			# parameter extraction
			actor1, actor2 = current_row[5], current_row[15]
			actor1_idx, actor2_idx = self.country_list.index(actor1), self.country_list.index(actor2)
			G, n_sources, n_articles, avg_tone = current_row[30], current_row[32], current_row[33], current_row[34]
			
			# edge estimation
			if G>0:
				edge = G + self.theta1*n_sources + self.theta2*n_articles + self.theta3*avg_tone
			elif G<0:
				edge = G + (-1)*(self.theta1*n_sources + self.theta2*n_articles) + self.theta3*avg_tone
			else:
				if avg_tone>0:
					edge = self.theta1*n_sources + self.theta2*n_articles + self.theta3*avg_tone
				elif avg_tone<0:
					edge = (-1)*(self.theta1*n_sources + self.theta2*n_articles) + self.theta3*avg_tone
				else:
					edge = 0
			# assuming undirect graph both edges must be equal
			self.matrix[actor1_idx, actor2_idx] += edge
			self.matrix[actor2_idx, actor1_idx] += edge

		# remove file
		if clean_after_computation:
			os.system(f"rm ./rawdata/{date}.{spec}.CSV")

	def _rescale(self):
		#self.matrix = np.divide(self.matrix, 10.0)
		raise NotImplementedError
		# no!!!!

	def _savecompress(self):
		print("Saving into ./networks ... ", end=" ")

		os.chdir("./networks")
		graph = f"./{self.date}_network.npy"
		np.save(graph, self.matrix)


		with zipfile.ZipFile(f"./{self.date}_network.zip", "w",
			compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
			zf.write(graph)

		os.system(f"rm {graph}")

		os.chdir("./..")


	def process_day(self):
		"""
		Single day matrix estimation by additive process
		"""
		self._initialize_adiacency_matrix()
		self._retrieve_daily_records()
		for record in self.record_list:
			self._download_process_single(record)
		#self._rescale()
		self._savecompress()
		print(f"Completed!", end="\n")
