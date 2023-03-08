import argparse

def str_cleaner(string: str):
		''' Needed for removing list tokens that remain in CL arguments.
			This was more efficient than using regex or other loop methods. '''
		string = str(string)
		string = string.strip()
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
	if 'http' not in url:
		url = 'http://' + url
	if url[-1] != '/':
		url = url + '/'

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

	return(url, num_processes, block, mode)


    
