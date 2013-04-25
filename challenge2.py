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
import pyrax

creds = os.path.expanduser("~/.rackspace_cloud_credentials")
pyrax.set_credential_file(creds)

cs = pyrax.cloudservers

srcserver = cs.servers.find(name="web1")

img = srcserver.create_image("web1-image")
image = cs.images.find(id=img)

while ( (image.status != "ACTIVE") ):
    print "Image status: ", image.status
    time.sleep(10)
    image = cs.images.get(image.id)

print "Image completed."

flavor = [flav for flav in cs.flavors.list()
              if flav.ram == 512][0]

print

print "Building server ",srcserver.name + "-clone"
print "Flavor: ", flavor
print

dstserver = cs.servers.create(srcserver.name+"-clone", image.id, flavor.id)
dstserver_pw = dstserver.adminPass


while ( (dstserver.status != "ACTIVE") ):
    print "Server status: ", dstserver.status
    time.sleep(10)
    dstserver = cs.servers.get(dstserver.id)

print
print "Server name: ", dstserver.name
print "Server IPs: ",str(dstserver.networks['public'][0]), " ", str(dstserver.networks['public'][1])
print "Server root password: ", dstserver_pw

