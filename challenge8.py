import os
import time
import argparse
import pyrax

index_page = """<head><title>API Challenge website</title></head>
    <body>
        Welcome to my API challenge website!<br>
    </body>"""

parser = argparse.ArgumentParser(description="Create a website hosted on CloudFiles.")
parser.add_argument("fqdn")
parser.add_argument("container")
args=parser.parse_args()

domain_name = args.fqdn.partition('.')[2]
host_name = args.fqdn.partition('.')[0]

creds = os.path.expanduser("~/.rackspace_cloud_credentials")
pyrax.set_credential_file(creds)

cdns = pyrax.cloud_dns
cf = pyrax.cloudfiles

print "Creating container {} and configuring it to serve {}...".format(args.container,args.fqdn)
cont=cf.create_container(args.container)
cf.store_object(args.container,"index.html",index_page)
cf.make_container_public(args.container,ttl=900)
cf.set_container_web_index_page(args.container,"index.html")
cont=cf.get_container(args.container)
print "Container configured."

print "Adding domain entry..."

dom=cdns.find(name=domain_name)

new_rec = [{
            "type" : "CNAME", 
            "name" : args.fqdn,
            "data" : cont.cdn_uri
          }]

add_result = dom.add_records(new_rec)

if add_result :
    print "Record {} created.".format(args.fqdn)
else :
    print "Error creating {} record.".format(args.fqdn)
