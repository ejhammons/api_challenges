import os
import time
import pyrax

server1_name = "web1"
server2_name = "web2"
server3_name = "web3"

creds = os.path.expanduser("~/.rackspace_cloud_credentials")
pyrax.set_credential_file(creds)

cs = pyrax.cloudservers

image = [img for img in cs.images.list()
              if "6.3" in img.name][0]
print "Image name: ", image

flavor = [flav for flav in cs.flavors.list()
              if flav.ram == 512][0]
print "Flavor: ", flavor

server1 = cs.servers.create(server1_name, image.id, flavor.id)
server2 = cs.servers.create(server2_name, image.id, flavor.id)
server3 = cs.servers.create(server3_name, image.id, flavor.id)

server1_pw = server1.adminPass
server2_pw = server2.adminPass
server3_pw = server3.adminPass

while ( (server1.status != "ACTIVE") or (server2.status != "ACTIVE") or (server3.status != "ACTIVE") ):
    print "Server status: ", server1.status, "|", server2.status, "|", server3.status
    time.sleep(10)
    server1 = cs.servers.get(server1.id)
    server2 = cs.servers.get(server2.id)
    server3 = cs.servers.get(server3.id)

print "Server name: ", server1.name
print "Server IP: ", str(server1.accessIPv4)
print "Server root password: ", server1_pw

print

print "Server name: ", server2.name
print "Server IPs: ", str(server2.accessIPv4)
print "server root password: ", server2_pw

print

print "Server name: ", server3.name
print "Server IPs: ", str(server3.accessIPv4)
print "server root password: ", server3_pw
