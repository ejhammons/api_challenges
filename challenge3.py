import os
import time
import argparse
import pyrax

parser = argparse.ArgumentParser(description='Upload a directory to CloudFiles.')
parser.add_argument('source_directory')
parser.add_argument('dest_container')
args=parser.parse_args()

source_directory = os.path.abspath(os.path.expanduser(args.source_directory))
dest_container = args.dest_container
if ( not os.path.exists(source_directory) ):
    print "Directory ", source_directory, " does not exist!"
    exit()
print "Directory exists."

creds = os.path.expanduser("~/.rackspace_cloud_credentials")
pyrax.set_credential_file(creds)

cf = pyrax.cloudfiles

container = cf.create_container(dest_container)

upload_key, total_bytes = cf.upload_folder(source_directory, dest_container)
print "Uploading ", source_directory, " to ", dest_container, " total bytes: ",total_bytes

uploaded_bytes = cf.get_uploaded(upload_key)
while ( uploaded_bytes != total_bytes ) :
    print "Bytes uploaded: ", uploaded_bytes
    time.sleep(10)
    uploaded_bytes = cf.get_uploaded(upload_key)

print "Upload complete!"
