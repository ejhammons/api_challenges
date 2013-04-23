import os
import sys
import time
import pyrax
import argparse

# Server names
server1_name = "web1"
server2_name = "web2"
server3_name = "web3"

# Configure command-line arguments
parser = argparse.ArgumentParser(
        description = "Create three servers behind an SSL-terminated load balancer")
# Path to SSL certificate and key
parser.add_argument("sslfile")
parser.add_argument("keyfile")
# Full domain name for load balancer
parser.add_argument("fqdn")
args=parser.parse_args()

# Verify SSL certificate file exists
sslfile_name = os.path.abspath(os.path.expanduser(args.sslfile))
if not os.path.exists(sslfile_name) :
    print "SSL certificate file {} does not exist!".format(sslfile_name)
    exit()
sslfile = open(sslfile_name)
sslcert = sslfile.read()

# Verify SSL key exists
keyfile_name = os.path.abspath(os.path.expanduser(args.keyfile))
if not os.path.exists(keyfile_name) :
    print "SSL key file {} does not exist!".format(keyfile_name)
    exit()
keyfile = open(keyfile_name)
sslkey = keyfile.read()


# Authenticate to the cloud
creds = os.path.expanduser("~/.rackspace_cloud_credentials")
pyrax.set_credential_file(creds)

# Obtain cloud objects needed to create the configuration
cs = pyrax.cloudservers
clb = pyrax.cloud_loadbalancers
cdns = pyrax.cloud_dns
cnw = pyrax.cloud_networks
cbs = pyrax.cloud_blockstorage

# Create dedicated network if it does not exist
ded_net = False
for net in cnw.list():
    if net.cidr == "172.16.16.0/24":
        ded_net = net
if not ded_net:
    ded_net = cnw.create("dedicated",cidr="172.16.16.0/24")
    print "Created dedicated network 172.16.16.0/24."
else:
    print "Dedicated network 172.16.16.0/24 already exists."
# All servers should have public and private addresses as well as the dedicated network
networks = ded_net.get_server_networks(public=True, private=True)

# Find the desired image (CentOS 6.3)
image = [img for img in cs.images.list()
              if "6.3" in img.name][0]
print "Image name: ", image.name

# Find the desired flavor (512MB)
flavor = [flav for flav in cs.flavors.list()
              if flav.ram == 512][0]
print "Flavor: ", flavor.name

# Create the servers
server1 = cs.servers.create(server1_name, image.id, flavor.id, networks=networks)
server2 = cs.servers.create(server2_name, image.id, flavor.id, networks=networks)
server3 = cs.servers.create(server3_name, image.id, flavor.id, networks=networks)

# Monitor server build progress
sys.stdout.write("Building servers: {:3}% {:3}% {:3}%".format(server1.progress, 
                                                              server2.progress, 
                                                              server3.progress))
sys.stdout.flush()
while ( (server1.status == "BUILD") or (server2.status == "BUILD") or (server3.status == "BUILD")):
    time.sleep(10)
    server1.get()
    server2.get()
    server3.get()
    sys.stdout.write("{}{:3}% {:3}% {:3}%".format("\b"*14,server1.progress,
                                                          server2.progress,
                                                          server3.progress))
    sys.stdout.flush()
print

if (server1.status == "ERROR") or (server2.status == "ERROR") or (server3.status == "ERROR"): 
    print "Error building server!"
    exit()

# Create block storage and attach to servers
print "Creating block storage and attaching it to the servers..."
server1_cbs = cbs.create(name="Server1_cbs", size=100)
server2_cbs = cbs.create(name="Server2_cbs", size=100)
server3_cbs = cbs.create(name="Server3_cbs", size=100)
server1_cbs.attach_to_instance(server1, "/dev/xvdb")
server2_cbs.attach_to_instance(server2, "/dev/xvdb")
server3_cbs.attach_to_instance(server3, "/dev/xvdb")

# Set up nodes and preferences for load balancer
node1 = clb.Node(address=server1.networks["private"][0], port=80, condition="ENABLED")
node2 = clb.Node(address=server2.networks["private"][0], port=80, condition="ENABLED")
node3 = clb.Node(address=server3.networks["private"][0], port=80, condition="ENABLED")

vip = clb.VirtualIP(type="PUBLIC")

# Create the load balancer
print "Creating load balancer..."
lb = clb.create("Website_LB", port=80, protocol="HTTP", nodes=[node1,node2,node3], virtual_ips=[vip])
while (lb.status == "BUILD"):
    time.sleep(10)
    lb.get()

# Configure load balancer for SSL termination
print "Adding SSL certificate to the load balancer..."
lb.add_ssl_termination(securePort=443, 
                       enabled=True, 
                       secureTrafficOnly=True, 
                       certificate=sslcert,
                       privatekey=sslkey)

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

print

print "Server name: ", server1.name
print "Server IP: ", str(server1.accessIPv4)
print "Server root password: ", server1.adminPass

print

print "Server name:", server2.name
print "Server IPs:", str(server2.accessIPv4)
print "server root password:", server2.adminPass

print

print "Server name:", server3.name
print "Server IPs:", str(server3.accessIPv4)
print "server root password:", server3.adminPass

print

lb_sslstatus = lb.get_ssl_termination()
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
print "Load balancer SSL termination:",
if lb_sslstatus['enabled']: 
    print "Enabled" 
else: 
    print "Disabled"
