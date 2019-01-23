# Classified Docs .

import time, threading, json, hashlib, os, logging
from getpass import getpass

logging.basicConfig(filename="logs.txt", level=logging.DEBUG, format=
	'%(asctime)s - %(levelname)s -%(message)s')

class Path(object):
	""" This represent a classified document.
	it has a method of adding the path,
	a method for deleting that document if it's needed."""

	def __init__(self):
		self.path = ""		# path for the file.
		self.dtime = 60	# time to deleting in secondes.
		self.inittime = ""	# time when object was created.
		# create the the thread to update() for this path.
		self.th_obj = threading.Thread(target=self.update)


	def __str__(self):
		""" the representation of the object."""
		pass

	def check_path(self):
		"checks if the path is valide."
		return os.path.exists(self.path)

	def get_inittime(self):
		""" time when object was created.
		get it from the TR_TIMES file if it was created before,
		else initialize the time to the current time.
		-Errors possible:
			--error 1: FileNotFoundError, means that this is the first
		path to be created, the database is not created yet.
			--error 2: KeyError, means that this path is new and doesn't
		exist in database. """
		try:
			with open("TR_TIMES.json") as f_obj:
				times = json.load(f_obj)
				self.inittime = times[self.path]

		except:
			# the file dosn't exist, or the path is not there.
			# this path is new then.
			self.inittime = time.time()	# set the creating time.
			logging.debug("Time added for first time!")

	def get_path(self):
		""" get the path from the user."""
		while True:
			self.path = input("Give the path for the file or folder:\n")
			if (self.check_path()):
				self.get_inittime()	# get the time of creation of the path.
				self.add_track()	# add path to database.
				# call update() as a second thread execution.
				logging.debug("Seconde Thread started for this path!")
				self.th_obj.start()
				print("The path is saved, and now tracked successfully!")
				break
			else:
				self.path = ""
				print("Path is incorrect! please try again!")
		logging.debug("Path initialized!")

	def add_track(self):
		""" add the path and the inittime into databases.
		if the TR_PATHS existed then TR_TIMES will also be existed.
		if not, then create them both."""
		try:
			with open("TR_PATHS.json",'r') as f_obj:# json for tracking paths.
				paths = json.load(f_obj)	# a list of previously added paths.

			paths.append(self.path)	# add the new path.
			with open("TR_PATHS.json", "w") as f_obj:
				json.dump(paths, f_obj)	# dump the new list back to database.
		except:
		# the file didn't exist before.
			with open("TR_PATHS.json",'w') as f_obj:	# create the file.
				json.dump([self.path], f_obj)	# list containing the 1st path.
			# create the file to save the inittime.
			# only for the first time.
			times = {}
			times[self.path] = self.inittime
			with open("TR_TIMES.json", "w") as f_obj:
				json.dump(times, f_obj)
		else:
			# the paths file exist, then the times file exist.
			# adding the new inittime for this path -object-.
			with open("TR_TIMES.json", 'r') as f_obj:
				times = json.load(f_obj)	# load the times dictionary.
			times[self.path] = self.inittime	# set inittime for the path.
			with open("TR_TIMES.json", 'w') as f_obj:
				json.dump(times, f_obj)
		logging.debug("{} added successfully!".format(self.path))

	def delete_file(self):
		""" delete the path and move it to deleted files database. """
		# import the the databases.
		
		with open("TR_PATHS.json", 'r') as f_obj:
			paths = json.load(f_obj)
		with open("TR_TIMES.json", 'r') as f_obj:
			dic = json.load(f_obj)
		# deleting from database and saving.
		os.remove(self.path)
		
		paths.remove(self.path)
		del dic[self.path]
		with open("TR_PATHS.json", 'w') as f_obj:
			json.dump(paths, f_obj)
		with open("TR_TIMES.json", 'w') as f_obj:
			json.dump(dic, f_obj)
		# adding the path to the deleted paths base.

		try:
			with open("DL_PATHS.json", 'r') as f_obj:
				paths = json.load(f_obj)
			paths.append(self.path)
			with open("DL_PATHS.json", 'w') as f_obj:
				json.dump(paths, f_obj)
		except:	# this file didn't exist.
			with open("DL_PATHS.json", 'w') as f_obj:
				json.dump([self.path], f_obj)	# list containing deleted files.
		logging.debug("Delete path: {}!".format(self.path))

	def update(self):
		""" update the time to check if the file should be 
		deleted or not.
		This is a second thread execution."""
		# check if there's time left, if not delete the file.
		while (time.time()-self.inittime < self.dtime):
			pass	# wait until the delete time(dtime) is elapsed.

		self.delete_file()	# delete the file.

class User(object):
	""" A user could manage many Path objects. """
	def __init__(self):
		# the list of the paths for this user.
		self.paths = []
		# always get the saved paths and update.
		self.get_paths()
		self.updates()	# update status for every path object.

	def get_paths(self):
		"""get the paths if there was any,
		otherwise return an empty list."""
		try:
			with open("TR_PATHS.json") as f_obj:
				self.paths = json.load(f_obj)
		except FileNotFoundError:
			self.paths = []


	def updates(self):
		"update status for every path object."
		# run through the paths in database.
		if self.paths:
			i = 0
			logging.debug("Updating tracks..")
			for path_str in self.paths:
				i += 1
				path_obj = Path()
				path_obj.path = path_str
				path_obj.get_inittime()	# get the corresponding inittime.
				# call update() for path object as a new thread execution.
				logging.debug("Starting this path Thread!")
				path_obj.th_obj.start()
				print("track {} updated successfully.".format(i))

	def status(self):
		"get status for every existing path, if there is any."
		if self.paths:
			for path_str in self.paths:
				path_obj = Path()
				path_obj.path = path_str
				path_obj.get_inittime()
				print("object created at: {}".format(path_obj.inittime))
				time_left = (time.time() - path_obj.inittime) - path_obj.dtime
				print("Classified file: {}".format(path_str))
				print("Time left before deleting: {}".format(time_left))
		else:
			print("There isn't any classified files yet.")

	def prompt(self, p):

		if p=='s':
			self.status()
		elif p=='a':
			path = Path()
			path.get_path()
			logging.debug("{} added successfully!".format(path.path))

	def set_up(self):
		"initialize the left time for all paths."
		logging.debug("set up the Dtime...")
		if self.paths:
			for path_str in self.paths:
				path = Path()
				path.path = path_str
				#get its stocked initial time.
				path.get_inittime()
				# re-initial it with current time.
				path.inittime = time.time()
				#load tha database and save the new time in.
				with open("TR_TIMES.json", 'r') as f_obj:
					dic = json.load(f_obj)
				
				dic[path.path] = path.inittime
				with open("TR_TIMES.json", 'w') as f_obj:
					json.dump(dic, f_obj)

			print("Time is well set up.")
			print("Time left for all your files: {} s".format(path.dtime))
			logging.debug("Time set_up, dtime now is: {}".format(path.dtime))
		else:
			print("There isn't any tracks currently.")
		

	def login(self):
		""" sign in or sign up if the user has not created an account yet. """
		try:
			with open("USERBASE.json") as f_obj:
				d = json.load(f_obj)
			while True:
				user_name = input("Enter your user-name: ").lower()
				try:
					saved_pass = d[user_name]
				except KeyError:
					print("incorrect user name! Please try again.")
					continue
				user_pass = getpass()
				passw = hashlib.sha1(user_pass.encode()).hexdigest()
				if passw == saved_pass:
					print("Access confirmed.")
					return False
				else:
					print("Access Denied !")

		except FileNotFoundError:
			# the first time the script run.
			print("You have to create an account first.")
			user_name = input("Enter your user name: ").lower()
			user_pass = getpass()
			passw = hashlib.sha1(user_pass.encode()).hexdigest()
			d = {user_name: passw}
			with open ("USERBASE.json", "w") as f_obj:
				json.dump(d, f_obj)
			print("Account created successfully !")
			logging.debug("Account ceated successfully!\n username:{}".format(user_name))

			# reset the deleting time.
			self.set_up()


u = User()
u.login()

while True:
	u.get_paths()
	p = input("To add a path tap 'a', 's' for status: ")
	u.prompt(p)
	if p == "q":
		break
logging.disable()
