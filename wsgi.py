import os, sys
sys.path.append('/var/www')
sys.path.append('/var/www/gingo')

os.chdir('/var/www')

from gingo import app as application

#if __name__=='__main__':
#	application.run('192.168.1.7', 5000)
