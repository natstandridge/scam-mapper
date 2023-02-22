import random
import requests
import time
import multiprocessing as mp
from multiprocessing import Process, Queue, Lock

import numpy as np

queue = Queue()


class DigitBlockParser:
	''' this class parses input strings and returns information
	about blocks of digits in the string'''

	def analyze_string(self, s: str, min_block_len: int, token: str) -> str:
		base_char = ""
		in_block = False
		block = ""
		blocks = []
		s += "\n"
		print(f"str: {s}")
		for char in s:
			if in_block: status_str = "in int block"
			else: status_str = "out of block"
			print(f"{status_str}: {block}")
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
			s = s.replace(b, token)

		return blocks, s



## 9 digits in s{integer}.onlinehome.us

def writer():
	lock = mp.Lock()
	lock.acquire()
	with open('good_domains.txt', 'a') as f:
		url = queue.get()
		f.write(url + '\n')
	f.close()
	lock.release()
	print(f"Writer process is finished writing {url}")

def checker(start_num, end_num):
	num = start_num
	while num < end_num:
		url = f"http://s{int(num)}.onlinehome.us"
		try:
			request = str(requests.get(url))
			
			if '20' in request:
				queue.put(url)
				writer()

			elif '30' in request:
				print(f'URL: {url} is not valid')
				
			else:
				print(f'URL: {url} is not valid and did not return 300-level code.')

		except Exception as e:
			print(e)
			
		num += 1
			

def main():

	num_processes = 100
	processes = []
	
	num_range = np.linspace(100000000, 1000000000, num_processes + 1)
	
	print(len(num_range))
	
	for i in range(num_processes):
		proc = mp.Process(target=checker, args=[num_range[i], num_range[i+1]])
		proc.start()
		processes.append(proc)
	
	for p in processes:
		p.join()

if __name__ == '__main__':
	# main()
	dbp = DigitBlockParser()

	blocks, s = dbp.analyze_string("123thisisatest76554aewf4344444", 2, "~")

	print(blocks)
	print(s)