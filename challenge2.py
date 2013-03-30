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

