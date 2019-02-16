import sys
import os
import shutil
## WARNING ##
# this script runs with elevated permissions #

def main():

	os.umask(0o077)
	
	if len(sys.argv) != 2:
		return
	user = sys.argv[0]
	mail = sys.argv[1]

	homes = {
		('/home/ucc/%s' % user, '/home/wheel/bin/skel/ucc'),
		('/away/ucc/%s' % user, '/home/wheel/bin/skel/away')
	}

	try:
		for home,skel in homes:
			shutil.copytree(skel,home,copy_function=copy)
			os.system('chown -R %s:gumby %s' % (user, home))


	except:
		exit(1)	

	home = homes[0][0]
	# set world writable (for webpage)
	os.system('chmod a+x %s' % home)
	os.system('chmod a+rX %s/public-html' % home)


	if (mailaddr != ""):
		forward = '%s/.forward' % home
		f = open(forward,"w")
		f.write(mailaddr)
		f.close()
		shutil.chown(forward,user,"gumby")
		os.chmod(forward, 0o644)


	
	

