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

anim=".oO"
anim_len=anim.count

server1_name = "web1"
server2_name = "web2"

creds = os.path.expanduser("~/.rackspace_cloud_credentials")
pyrax.set_credential_file(creds)

cs = pyrax.cloudservers
clb = pyrax.cloud_loadbalancers

image = [img for img in cs.images.list()
              if "6.3" in img.name][0]
print "Image name: ", image

flavor = [flav for flav in cs.flavors.list()
              if flav.ram == 512][0]
print "Flavor: ", flavor

server1 = cs.servers.create(server1_name, image.id, flavor.id)
server2 = cs.servers.create(server2_name, image.id, flavor.id)

ani_i=0
ani_chr=anim[ani_i]

sys.stdout.write("Building servers: {}{}".format(ani_chr,ani_chr))
sys.stdout.flush()
while ( (server1.status == "BUILD") or (server2.status == "BUILD") ):
    time.sleep(10)
    ani_chr=anim[ani_i]
    server1.get()
    server2.get()
    sys.stdout.write("\b\b")
    if server1.status == "ERROR" :
        sys.stdout.write("!")
    elif server1.status == "ACTIVE":
        sys.stdout.write("*")
    else:
        sys.stdout.write(ani_chr)
    if server2.status == "ERROR" :
        sys.stdout.write("!")
    elif server2.status == "ACTIVE":
        sys.stdout.write("*")
    else:
        sys.stdout.write(ani_chr)
    sys.stdout.flush()
    ani_i=ani_i+1
    if ani_i>=len(anim): ani_i=0
print

node1 = clb.Node(address=server1.networks["private"][0], port=80, condition="ENABLED")
node2 = clb.Node(address=server2.networks["private"][0], port=80, condition="ENABLED")

vip = clb.VirtualIP(type="PUBLIC")

lb = clb.create("Website_LB", port=80, protocol="HTTP", nodes=[node1,node2], virtual_ips=[vip])

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
