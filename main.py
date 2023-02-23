import requests
import multiprocessing as mp
from multiprocessing import Process, Queue, Lock
import numpy as np
import argparse

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

	def _writer(self):
		''' Private method for writing from queue. '''
		self.lock.acquire()
		with open('verified_domains.txt', 'a') as f:
			url = self.queue.get()
			f.write(url + '\n')
		f.close()
		self.lock.release()
		print(f"Writer process is finished writing {url}")

	def checker(self, url_f_string, start_num, end_num):
		''' Takes in url_f_string, start_num, and end_num to run through every possible URL combo and run the writer if it has data. '''
		num = start_num
		while num < end_num:
			url = url_f_string
			url = eval(url) ## evaluating to insert num into url_f_string
			try:
				request = str(requests.get(url))
				
				if '20' in request:
					print(f'{Colors.GREEN}Valid URL Found: {url}{Colors.ENDC}')
					self.queue.put(url)
					self._writer()

				elif '30' in request:
					print(f'URL: {url} is not valid and returned 300-level code.')
					
				else:
					print(f'URL: {url} is not valid and did not return 300-level code.')

			except requests.exceptions.RequestException as e: ## have to ignore request exceptions to pass on pages that are timing out
				#print(e)
				print(f"URL: {url} is not valid.")
				
			num += 1
				
def main(num_processes=500):

	parser = argparse.ArgumentParser()

	parser.add_argument("-u", "--url", required=False, nargs=1, type=str, help="For adding a URL via command-line.") ## -u flag followed by URL
	parser.add_argument("-p", "--proc", required=False, nargs=1, type=int, help="For specifying a number of processes.")

	args = parser.parse_args()

	if args.url == None:
		url = input("\nFormat should be http:// or https://scamurl1423523.com\nPlease enter the scam URL you want to map: ") ## prompts for URL to be provided if no CL argument for -u was provided
	else:
		url = str(args.url).replace("'", "").replace("[","").replace("]","") ## cleaning string because it retains tokens from list

	if args.proc != None:
		num_processes = int(str(args.proc).replace("'", "").replace("[","").replace("]","")) ## sets new num_processes if a CL argument was passed for -p
	else:
		pass

	dbp = DigitBlockParser()
	num_block, url_f_string = dbp.analyze_string(url, 3) ## gets block of numbers larger than 3 out of url, and creates f string based on url with numbers removed (for iterating)
	num_block = str(num_block).replace("'", "").replace("[","").replace("]","") ## have to remove tokens left over from list
	num_of_nums = len(str(num_block)) ## this is the number of digits we need to start with (num_of_nums + 1 will be the end_num)

	start_num_string = '1'
	end_num_string = '1'

	for i in range(num_of_nums-1):	## loop for generating start number with proper number of digits
		start_num_string += '0'

	for i in range(num_of_nums):	## loop for generating end number with proper number of digits
		end_num_string += '0'

	start_num, end_num = int(start_num_string), int(end_num_string)
	num_range = np.linspace(start_num, end_num - 1, num_processes + 1)
	mapper = Mapper()

	processes = []
	
	for i in range(num_processes):
		proc = Process(target=mapper.checker, args=[url_f_string, num_range[i], num_range[i+1]])
		proc.start()
		processes.append(proc)
	
	for p in processes:
		p.join()

if __name__ == '__main__':
	main()