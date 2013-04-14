import os
import time
import argparse
import pyrax

parser = argparse.ArgumentParser(description='Upload a directory to CloudFiles.')
parser.add_argument('dest_container')
args=parser.parse_args()

dest_container = args.dest_container

creds = os.path.expanduser("~/.rackspace_cloud_credentials")
pyrax.set_credential_file(creds)

cf = pyrax.cloudfiles

container = cf.create_container(dest_container)

container.make_public(ttl=900)

print "Created container",container.name
print "CDN status:",container.cdn_enabled
print "TTL:",container.cdn_ttl
print "URI:",container.cdn_uri
print "SSL URI:",container.cdn_ssl_uri
print "Streaming URI:",container.cdn_streaming_uri
print "iOS URI:",container.cdn_ios_uri
