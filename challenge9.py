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

import os
import time
import argparse
import pyrax
import sys

parser = argparse.ArgumentParser(description="Create a new A record in a subdomain.")
parser.add_argument("fqdn")
parser.add_argument("image")
parser.add_argument("flavor")
args=parser.parse_args()

domain_name = args.fqdn.partition('.')[2]
host_name = args.fqdn.partition('.')[0]

creds = os.path.expanduser("~/.rackspace_cloud_credentials")
pyrax.set_credential_file(creds)

cs = pyrax.cloudservers
cdns = pyrax.cloud_dns

image = [img for img in cs.images.list()
            if args.image in img.name][0]
print "Image name:",image.name

flavor = [flav for flav in cs.flavors.list()
             if args.flavor in flav.name][0]
print "Flavor:",flavor.name

server = cs.servers.create(args.fqdn, image.id, flavor.id)

sys.stdout.write("Building server: {:3}%".format(server.progress))
sys.stdout.flush()
while (server.status == "BUILD"):
    time.sleep(10)
    server.get()
    sys.stdout.write("\b\b\b\b{:3}%".format(server.progress))
    sys.stdout.flush()

print

if server.status == "ERROR":
    print "Error building server!"
    exit()

print "Build complete, adding DNS entry..."

dom=cdns.find(name=domain_name)

new_rec = [{
            "type" : "A", 
            "name" : args.fqdn,
            "data" : str(server.accessIPv4)
          }]

add_result = dom.add_records(new_rec)

if add_result :
    print "Record {} created.".format(args.fqdn)
else :
    print "Error creating {} record.".format(args.fqdn)

print "Server name:", server.name
print "Server IP:", str(server.accessIPv4)
print "Server root password:",server.adminPass
