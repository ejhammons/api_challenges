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
