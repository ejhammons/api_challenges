import sys
import os
import time
import pyrax

creds = os.path.expanduser("~/.rackspace_cloud_credentials")
pyrax.set_credential_file(creds)

cdb = pyrax.cloud_databases

inst = cdb.create('challenge_db', flavor=1, volume=1)
sys.stdout.write("Building instance:")
sys.stdout.flush()
while (inst.status == "BUILD") :
    sys.stdout.write(".")
    sys.stdout.flush()
    time.sleep(10)
    inst.get()

print "Done"

db = inst.create_database('wp-site')
print "Created database", db.name

user_pw = "wp4ever"
user = inst.create_user(name="wp-admin", password=user_pw, database_names=[db])
print "Created user", user.name

print
print
print "Instance name:",inst.name
print "Instance hostname:",inst.hostname
print "Database name:",db.name
print "Username:",user.name
print "User password:",user_pw
