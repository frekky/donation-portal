import sys
import os
import shutil
import subprocess


   ###     ######  ##     ## ######## ##     ## ##    ##  ######   
  ## ##   ##    ## ##     ##    ##    ##     ## ###   ## ##    ##  
 ##   ##  ##       ##     ##    ##    ##     ## ####  ## ##        
##     ## ##       #########    ##    ##     ## ## ## ## ##   #### 
######### ##       ##     ##    ##    ##     ## ##  #### ##    ##  
##     ## ##    ## ##     ##    ##    ##     ## ##   ### ##    ##  
##     ##  ######  ##     ##    ##     #######  ##    ##  ######   

		# this script runs with elevated permissions #
			# be very careful with what you do #

def main():

	os.umask(0o077)

	if len(sys.argv) != 3:
		exit(1)
	user = sys.argv[1]
	mail = sys.argv[2]

	# abort if user does not exist
	if subprocess.call(["id", user], stderr=subprocess.DEVNULL) != 0:
		exit(1)

	homes = {
		('/home/ucc/%s' % user, '/home/wheel/bin/skel/ucc'),
		('/away/ucc/%s' % user, '/home/wheel/bin/skel/away')
	}
	# make homes
	try:
		for home,skel in homes:
			shutil.copytree(skel,home,copy_function=copy)
			os.system('chown -R %s:gumby %s' % (user, home))

		home = homes[0][0]
		# set world writable (for webpage)
		os.system('chmod a+x %s' % home)
		os.system('chmod a+rX %s/public-html' % home)
	except:
		exit(1)

	# write .forward
	try:
		if (mailaddr != ""):
			forward = '%s/.forward' % home
			f = open(forward,"w")
			f.write(mailaddr)
			f.close()
			shutil.chown(forward,user,"gumby")
			os.chmod(forward, 0o644)
	except:
		exit(1)


if __name__ == "__main__":
	main()
	exit(0)




