import requests
from multiprocessing import Process, Queue, Lock
import numpy as np
from helpers import *

class Colors:
    """ Colors for differentiating between messages. Use like so: f"{colors.GREEN}My green text{colors.ENDC}".  """
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class DigitBlockParser:
	''' This class parses input strings and returns information about blocks of digits in the string. '''
	def analyze_string(self, s: str, min_block_len: int) -> str:
		in_block = False
		block = ""
		blocks = []
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
			s = s.replace(b, '{int(num)}') ## inserts fstring compatible num variable that is always converted to int just in case

		return(blocks, f'f"""{s}"""') ## fstring hack that allows us to turn a normal string into an fstring

class Explorer:
	''' Explores URL possibilities and records the ones that are valid. '''
	def __init__(self, mode='subdomain', wordlist='wordlists/common.txt'):
		self.queue = Queue()
		self.lock = Lock()
		self.mode = mode
		self.wordlist = wordlist

	def __writer(self):
		''' Acquires lock, gets URL from queue, and then writes to the file and releases lock. '''
		self.lock.acquire()
		with open('verified_domains.txt', 'a') as f:
			url = self.queue.get()
			f.write(url + '\n')
		f.close()
		self.lock.release()

	def __page_iterator(self, url):
		''' Returns a list of pages for the provided URL based on self.wordlist '''

		with open(self.wordlist, 'r') as f:
			directories = f.read().splitlines()
		f.close()

		page_list = []

		for directory in directories:
			page_list.append(url + directory)

		return(page_list)

	def __checker(self, request, url):
		''' Checks codes returned from request to determine validity. '''
		if '20' in request:
			print(f'{Colors.GREEN}Valid URL Found: {url}{Colors.ENDC}')
			self.queue.put(url)
			self.__writer()

		elif '30' in request:
			print(f'URL: {url} is not valid and returned 300-level code.')
			
		else:
			print(f'URL: {url} is not valid and did not return 300-level code.')

	def __requester(self, url):
		''' Performs the request on the URL and runs checker to check codes. '''

		if self.mode == 'directory':
			try:
				request = str(requests.get(url))
				self.__checker(request, url)
			except:
				print(f'URL: {url} is not valid - the request failed.')
			
			page_list = self.__page_iterator(url)

			for page in page_list:
				try:
					request = str(requests.get(page))
					self.__checker(request, page)
				except:
					print(f'URL: {url} is not valid - the request failed in directory mode.')
				
		else:
			try:
				request = str(requests.get(url))
				self.__checker(request, url)
			except:
				print(f'URL: {url} is not valid - the request failed.')
		
	def handler(self, url_fstring, start_num, end_num):
		''' Handler that takes care of fstring evaluation, and looping through each number. '''
		num = start_num
	
		while num < end_num:
			url = url_fstring
			url = eval(url)

			self.__requester(url)

			num += 1

def main(num_processes=100):

	url, num_processes, block, mode = cli_handler()

	dbp = DigitBlockParser()
	num_block, url_fstring = dbp.analyze_string(url, block)
	num_block = str_cleaner(num_block)
	num_of_nums = len(str(num_block)) ## this is the number of digits we need to start with

	## intializing first digit of each number
	start_num_string = '1'
	end_num_string = '1' 

	for i in range(num_of_nums-1):	## loop for generating start number with proper number of digits
		start_num_string += '0'

	for i in range(num_of_nums):	## loop for generating end number with proper number of digits
		end_num_string += '0'

	start_num, end_num = int(start_num_string), int(end_num_string)
	num_range = np.linspace(start_num, end_num - 1, num_processes + 1) ## returns num_processes + 1 of evenly spaced samples
	explorer = Explorer(mode)

	processes = []
	
	for i in range(num_processes):
		''' With each process spawned, pass i as start_num and i+1 as end_num as indices to num_range to get each set of evenly spaced numbers from linspace. '''
		proc = Process(target=explorer.handler, args=[url_fstring, num_range[i], num_range[i+1]])
		proc.start()
		processes.append(proc)
        	
	for p in processes:
		p.join()

if __name__ == '__main__':
	main()