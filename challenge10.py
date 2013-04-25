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
import sys
import time
import pyrax
import argparse

# Server names
server1_name = "web1"
server2_name = "web2"

# Custon Load Balancer webpage
error_html = "<html><body>Guru Meditation #22!</body></html>"

# Configure command-line arguments
parser = argparse.ArgumentParser(
        description = "Create two servers preloaded with SSH keys and a load balancer with a custom error page")
# Path to SSH key
parser.add_argument("keyfile")
# Full domain name for load balancer
parser.add_argument("fqdn")
args=parser.parse_args()

# Verify key file exists
keyfile_name = os.path.abspath(os.path.expanduser(args.keyfile))
if not os.path.exists(keyfile_name) :
    print "Keyfile {} does not exist!".format(keyfile_name)
    exit()
# Add keyfile to dictionary for upload to servers
keyfile = open(keyfile_name)
files = {"/root/.ssh/authorized_keys": keyfile}

# Authenticate to the cloud
creds = os.path.expanduser("~/.rackspace_cloud_credentials")
pyrax.set_credential_file(creds)

# Obtain cloud objects needed to create the configuration
cs = pyrax.cloudservers
clb = pyrax.cloud_loadbalancers
cdns = pyrax.cloud_dns
cf = pyrax.cloudfiles

# Find the desired image (CentOS 6.3)
image = [img for img in cs.images.list()
              if "6.3" in img.name][0]
print "Image name: ", image.name

# Find the desired flavor (512MB)
flavor = [flav for flav in cs.flavors.list()
              if flav.ram == 512][0]
print "Flavor: ", flavor.name

# Create the servers
server1 = cs.servers.create(server1_name, image.id, flavor.id, files=files)
server2 = cs.servers.create(server2_name, image.id, flavor.id, files=files)

# Monitor server build progress
sys.stdout.write("Building servers: {:3}% {:3}%".format(server1.progress,server2.progress))
sys.stdout.flush()
while ( (server1.status == "BUILD") or (server2.status == "BUILD") ):
    time.sleep(10)
    server1.get()
    server2.get()
    sys.stdout.write("{}{:3}% {:3}%".format("\b"*9,server1.progress,server2.progress))
    sys.stdout.flush()
print

if (server1.status == "ERROR") or (server2.status == "ERROR"): 
    print "Error building server!"
    exit()

# Set up nodes and preferences for load balancer
node1 = clb.Node(address=server1.networks["private"][0], port=80, condition="ENABLED")
node2 = clb.Node(address=server2.networks["private"][0], port=80, condition="ENABLED")

vip = clb.VirtualIP(type="PUBLIC")

# Create the load balancer
print "Creating load balancer..."
lb = clb.create("Website_LB", port=80, protocol="HTTP", nodes=[node1,node2], virtual_ips=[vip])
while (lb.status == "BUILD"):
    time.sleep(10)
    lb.get()

# Configure monitoring on load balancer and set the custom error page
print "Adding monitors and error page to load balancer..."
lb.add_health_monitor(type="HTTP", delay=10, timeout=10,
        attemptsBeforeDeactivation=3, path="/",
        statusRegex="^[234][0-9][0-9]$",
        bodyRegex=".*")
lb.get()
while (lb.status != "ACTIVE"):
    time.sleep(10)
    lb.get()
lb.set_error_page(error_html)

# Set up DNS record
print "Creating DNS entry..."
domain_name = args.fqdn.partition('.')[2]
dom = cdns.find(name=domain_name)
new_rec = [{
            "type" : "A",
            "name" : args.fqdn,
            "data" : str(lb.virtual_ips[0].address)
          }]
add_result = dom.add_records(new_rec)

if add_result:
    print "Record {} created.".format(args.fqdn)
else :
    print "Error creating {} record.".format(args.fqdn)

# Back up error page to cloudfiles
container = cf.create_container(args.fqdn)
cf.store_object(args.fqdn,"error.html",error_html)

print

print "Server name: ", server1.name
print "Server IP: ", str(server1.accessIPv4)
print "Server root password: ", server1.adminPass

print

print "Server name:", server2.name
print "Server IPs:", str(server2.accessIPv4)
print "server root password:", server2.adminPass

print

print "Load balancer name:",lb.name
print "Load balancer status:",lb.status
print "Load balancer IPs:",
for ip in lb.virtual_ips:
    print ip.address,
print
print "Load balancer nodes:",
for n in lb.nodes:
    print n.address,
print
print "Load balancer algorithm:",lb.algorithm
print "Load balancer protocol:",lb.protocol
