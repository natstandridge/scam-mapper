import requests
import multiprocessing as mp
from multiprocessing import Process, Queue, Lock
import numpy as np
import argparse
import time

class DigitBlockParser:
	''' this class parses input strings and returns information
	about blocks of digits in the string'''

	def analyze_string(self, s: str, min_block_len: int) -> str:
		base_char = ""
		in_block = False
		block = ""
		blocks = []
		s += "\n"
		for char in s:
			if str(char).isdigit():
				block += char
				if not in_block:
					in_block = True
			else:
				if in_block:
					in_block = False
					if len(block) > min_block_len:
						blocks.append(block)
					block = ""
				else:
					pass
		
		blocks.sort(key=len)

		for b in blocks:
			s = s.replace(b, '{int(num)}')
		
		s = s[:-1]

		return blocks, f'f"""{s}"""' ## f string hack


class Mapper(DigitBlockParser):
	def __init__(self):
		self.queue = Queue()
		self.lock = Lock()

	def writer(self):
		self.lock.acquire()
		with open('verified_domains.txt', 'a') as f:
			url = self.queue.get()
			f.write(url + '\n')
		f.close()
		self.lock.release()
		print(f"Writer process is finished writing {url}")

	def checker(self, url_f_string, start_num, end_num):
		''' 
		Takes in url_f_string, start_num, and end_num to run through every possible URL combo and run the writer if it has data.
		
		'''
		num = start_num
		while num < end_num:
			url = url_f_string
			url = eval(url) ## evaluating to insert num into url_f_string
			try:
				request = str(requests.get(url))
				time.sleep(3)
				
				if '20' in request:
					self.queue.put(url)
					self.writer()

				elif '30' in request:
					print(f'URL: {url} is not valid')
					
				else:
					print(f'URL: {url} is not valid and did not return 300-level code.')

			except requests.exceptions.RequestException as e: ## have to ignore request exceptions to pass on pages that are timing out
				#print(e)
				print(f"URL: {url} is not valid.")
				
			num += 1
				
def main(num_processes=10):

	parser = argparse.ArgumentParser()
	parser.add_argument("-u", nargs=1, type=str) ## -u flag followed by URL
	args = parser.parse_args()

	if getattr(args, "u") == None:
		url = input("\nFormat should be http:// or https://scamurl1423523.com\nPlease enter the scam URL you want to map: ")

	else:
		url = str(getattr(args, "u"))
		url = url.replace("'", "").replace("[","").replace("]","") ## cleaning string because it retains tokens from list

	dbp = DigitBlockParser()
	num_block, url_f_string = dbp.analyze_string(url, 3) ## gets block of numbers larger than 3 out of url, and creates f string based on url with numbers removed (for iterating)
	num_block = str(num_block).replace("'", "").replace("[","").replace("]","") ## have to remove tokens left over from list

	num_of_nums = len(str(num_block)) ## this is the number of digits we need to start with (num_of_nums + 1 will be the end_num)

	start_num_string = '1'
	end_num_string = '1'

	for i in range(num_of_nums-1):
		start_num_string += '0'

	for i in range(num_of_nums):
		end_num_string += '0'

	start_num, end_num = int(start_num_string), int(end_num_string)

	processes = []
	
	num_range = np.linspace(start_num, end_num - 1, num_processes + 1)

	mapper = Mapper()
	
	for i in range(num_processes):
		proc = Process(target=mapper.checker, args=[url_f_string, num_range[i], num_range[i+1]])
		proc.start()
		processes.append(proc)
	
	for p in processes:
		p.join()

if __name__ == '__main__':
	main()