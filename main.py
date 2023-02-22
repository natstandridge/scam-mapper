import requests
import multiprocessing as mp
from multiprocessing import Process, Queue, Lock
import numpy as np
import argparse

class Mapper:
	def __init__(self):
		self.queue = Queue()
		self.lock = Lock()

	def writer(self):
		self.lock.acquire()
		with open('good_domains.txt', 'a') as f:
			url = self.queue.get()
			f.write(url + '\n')
		f.close()
		self.lock.release()
		print(f"Writer process is finished writing {url}")

	def checker(self, start_num, end_num):
		num = start_num
		while num < end_num:
			url = f"http://s{int(num)}.onlinehome.us"
			try:
				request = str(requests.get(url))
				
				if '20' in request:
					self.queue.put(url)
					self.writer()

				elif '30' in request:
					print(f'URL: {url} is not valid')
					
				else:
					print(f'URL: {url} is not valid and did not return 300-level code.')

			except Exception as e:
				print(f"URL: {url} is not valid.")
				
			num += 1
				
	def main(self):

		parser = argparse.ArgumentParser()
		parser.add_argument("-u", nargs=1, type=str) ## -u flag followed by URL
		args = parser.parse_args()
		url = str(getattr(args, "u"))
		url = url.replace("'", "").replace("[","").replace("]","")

		num_processes = 10
		processes = []
		
		num_range = np.linspace(100000000, 1000000000, num_processes + 1)
		
		for i in range(num_processes):
			proc = Process(target=self.checker, args=[num_range[i], num_range[i+1]])
			proc.start()
			processes.append(proc)
		
		for p in processes:
			p.join()

if __name__ == '__main__':
	mapper = Mapper()
	mapper.main()
