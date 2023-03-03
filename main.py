import requests
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

		return blocks, f'f"""{s}"""' ## fstring hack that allows us to turn a normal string into an fstring

class Explorer:
	def __init__(self, mode='subdomain', wordlist='wordlists/common.txt'):
		self.queue = Queue()
		self.lock = Lock()
		self.mode = mode
		self.wordlist = wordlist

	def _writer(self):
		''' Acquires lock, gets URL from queue, and then writes to the file and releases lock. '''
		self.lock.acquire()
		with open('verified_domains.txt', 'a') as f:
			url = self.queue.get()
			f.write(url + '\n')
		f.close()
		self.lock.release()
		print(f"Writer process is finished writing {url}")

	def _page_iterator(self, url):
		''' Returns a list of pages to check for the given URL. '''
		
		for extension in open('extensions.txt', 'r').read().splitlines():
			if extension in url:
				page_start_index = url.index(extension) + len(extension) + 1
				url_without_page = url[:page_start_index]
				break
			else:
				continue

		with open(self.wordlist, 'r') as f:
			directories = f.read().splitlines()
		f.close()

		page_list = []

		for directory in directories:
			page_list.append(url_without_page + directory)

		return page_list

	def _requester(self, url):
		''' Takes in url_fstring, start_num, and end_num
			to run through every possible URL combo and run
			the writer if it has data. '''

		def check(request, url):
			if '20' in request:
				print(f'{Colors.GREEN}Valid URL Found: {url}{Colors.ENDC}')
				self.queue.put(url)
				self._writer()

			elif '30' in request:
				print(f'URL: {url} is not valid and returned 300-level code.')
				
			else:
				print(f'URL: {url} is not valid and did not return 300-level code.')

		request = str(requests.get(url))
		check(request, url)
		
		if self.mode == 'directory':
			page_list = self._page_iterator(url)
			for page in page_list:
				request = str(requests.get(page))
				check(request, page)
				
	def handler(self, url_fstring, start_num, end_num):
		''' Handler that takes care of fstring evaluation, and looping through each number. '''
		num = start_num
	
		while num < end_num:
			url = url_fstring
			url = eval(url)

			if 'http' not in url:
				url = 'http://' + url
			if url[-1] != '/':
					url = url + '/'

			try:
				self._requester(url)
			except requests.exceptions.RequestException as e: ## have to ignore request exceptions to pass on pages that are timing out
				#print(e)
				print(f"URL: {url} is not valid.")

			num += 1

def str_cleaner(string: str):
		''' Needed for removing list tokens that remain in CL arguments.
			This was more efficient than using regex or loop methods. '''
		string = str(string)
		for ch in ["'","]","["]:
			string = string.replace(ch, "")
		return string
	
def cli_handler():
	parser = argparse.ArgumentParser()

	parser.add_argument("-u", "--url", required=False, nargs=1, type=str, help="For adding a URL via command-line.")
	parser.add_argument("-p", "--proc", required=False, nargs=1, type=int, help="For specifying a number of processes for multiprocessing to spawn.")
	parser.add_argument("-b", "--block", required=False, nargs=1, type=int, help="The minimum digit block length to bruteforce.")
	parser.add_argument("-m", "--mode", required=False, nargs=1, type=str, help="Accepts 'directory' or 'subdomain'. Subdomain mode is the default.")

	args = parser.parse_args()

	if args.url == None:
		url = input("Please enter the scam URL you want to map: ")
	else:
		url = str_cleaner(args.url)
	if args.proc == None:
		num_processes = int(input("Enter the number of processes you would like multiprocessing to spawn: "))
	else:
		num_processes = int(str_cleaner(args.proc))
	if args.block == None:
		block = int(input("Enter the minimum digit block length you would like to target for bruteforcing: "))
	else:
		block = int(str_cleaner(args.block))
	if args.mode == None:
		mode = input("Specify a mode (subdomain or directory): ")
		while (mode != 'subdomain') and (mode != 'directory'):
			mode = input("Invalid input. Specify a mode (subdomain or directory): ")
	else:
		mode = str_cleaner(args.mode)
		while (mode != 'subdomain') and (mode != 'directory'):
			mode = input("Invalid input. Specify a mode (subdomain or directory): ")

	return url, num_processes, block, mode

def main(num_processes=500):

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