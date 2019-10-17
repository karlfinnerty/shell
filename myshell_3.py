import sys
import os
import subprocess
import cmd
import time
import json
from colours import Colours


#the main shell class
class MyShell(cmd.Cmd):
	shell = os.environ['PWD']
	cmd.Cmd.intro = "Hello and welcome to KarlShell! (V1.3.1 running from {})".format(shell)
	cmd.Cmd.prompt = Colours.cyan('(KarlShell:') + Colours.pink(os.getcwd() + ') ')

	dirs = os.getcwd().split('/')
	home = dirs[1]

	#changes the directory
	#is designed to take either the full path starting from the home directory e.g. /home/user/Documents, or take a single subdirectory of the cwd e.g. /Documents
	def do_cd(self, line):											
		#error handling ensures wrong directory path or permission denial will not crash shell
		try:									
			if self.home in line: 									
				os.chdir('/' + line)
			else:
				os.chdir(os.getcwd() + '/' + line)

		except FileNotFoundError:
			print(Colours.red("Invalid directory: {}".format(line)))

		except Exception as e:
			print(e)

		#update the prompt to show the new directory
		cmd.Cmd.prompt = Colours.cyan('(KarlShell:') + Colours.pink(os.getcwd() + ') ')		

	#displays current working directory
	def do_pwd(self, line):											
		print(os.getcwd())

	#lists and displays all subdirectories and files
	# if redirect is True, pass output onto output_redirect method
	def do_dir(self, line):
		if self.check_redirect(line) == False:
			print("\n".join(os.listdir()))
		else:
			out = ("\n".join(os.listdir()))
			self.output_redirect(line, out)

	#lists and displays environmental strings
	def do_environ(self, line): 
		if self.check_redirect(line) == False:
			for k, v in os.environ.items():
				print(k + ": " + v)
		else:
			out = []
			for k, v in os.environ.items():
				out.append(k + ": " + v)
			out = "\n".join(out)
			self.output_redirect(line, out)

	#outputs the argument supplied by user
	def do_echo(self, line):
		tokens = self.get_tokens(line)
		if self.check_redirect(line) == False:										
			print(line + '\n')
		else:
			out = (' '.join(tokens[0:-2]))
			self.output_redirect(line, out)

	#opens manual located in readme file and displays to user twenty lines at a time
	def do_help(self, line):
		try:
			if self.check_redirect(line) == False:								
				with open(self.shell + "/readme", "r") as f:
					i = 2
					j = 22
					help_lines = f.read().split("\n")
					next_twenty = '\n'.join(help_lines[i:j])
					while j < len(help_lines):
						next_twenty = '\n'.join(help_lines[i:j])
						print(next_twenty)
						input()
						i += 20
						j += 20
			else:
				with open(self.shell + "/readme", "r") as f:
					out = f.read()
				self.output_redirect(line, out)
		except:
			(print("There appears to be a problem with the help manual..."))

	#clears the display by checking terminal size and printing new lines
	def do_clr(self, line):											
		rows, columns = os.popen('stty size', 'r').read().split()
		for i in range(0, int(rows)):
			print("\n")

	#pauses operation of the shell until enter is pressed
	def do_pause(self, line):
		input("Press enter to resume..." + "\n")

	#an extra internal command I added to help with testing
	def do_sleep(self, line):
		try:
			time.sleep(int(line))
		except:
			print("Exception!")

	#exits the shell
	def do_quit(self, line):
		sys.exit()

	#default action for when user inputs an empty line
	def emptyline(self):
		print("")

	#default action for commands that are not defined
	def default(self, line):
		tokens = self.get_tokens(line)
		if tokens[-1] == "&":
			self.background_exec(line)
		else:
			self.invoke(line)

	#if user enters a command that is not among the internal commands, check if the command is invocation of external programs and execute them
	def invoke(self, line):
		line = self.get_tokens(line)
		pid = os.fork()

		if pid > 0:
			wait_pid = os.waitpid(pid, 0)
		else:	
			try:
				os.execvp(line[0], line)
			except FileNotFoundError:
				print(Colours.red(" '{}' not found. Type 'help' for shell documentation.".format(' '.join(line))))
				self.do_quit('')
			except:
				print("Exception!")
				self.do_quit('')

	#execute program defined in line as background process
	def background_exec(self, line):
		line = self.get_tokens(line)
		subprocess.Popen(line)

	#check if user is attempting to redirect output
	def check_redirect(self, line):
		tokens = self.get_tokens(line)
		if len(tokens) > 0 and (">" in tokens or ">>" in tokens):
			return True
		else:
			return False

	#determine whether user wants to append or truncate and find position of new file name
	def output_redirect(self, line, output):
		tokens = self.get_tokens(line)
		i = 0
		while i < len(tokens) and (tokens[i-1] != ">" or tokens[i-1] != ">>"):
			if tokens[i] == ">":
				self.truncate(line, output, i)
			elif tokens[i] == ">>":
				self.append(line, output, i)
			i += 1

	#get name of new file by using position supplied by output_redirect, and either create new file or truncate existing
	def truncate(self, line, output, position):
		i = position
		tokens = self.get_tokens(line)
		with open(tokens[i+1], "w") as f:
			f.write(output)

	#same as truncate method, except append to existing file
	def append(self, line, output, position):
		i = position
		tokens = self.get_tokens(line)
		with open(tokens[i+1], "a") as f:
			f.write("\n" + output)

#a simple method for splitting a line into tokens
	def get_tokens(self, line):
		tokens = line.split()
		return tokens

#main is where the program decides whether to allow normal user input, or whether to take input from a batch file.
#if a batch file is detected, it will iterate through and execute each command in the file before quitting the shell.	
def main():
	if len(sys.argv) > 1:	
		with open (sys.argv[1], "r") as f:
			commands = f.readlines()						

		for command in commands:								
			MyShell().onecmd(command)
		MyShell.onecmd(MyShell.do_quit(MyShell, ''))									

	else:
		MyShell().cmdloop()										

if __name__ == '__main__':
	main()
