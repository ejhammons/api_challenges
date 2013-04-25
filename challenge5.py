# Copyright 2013 Jason Hammons

# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

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
