# PDC_scripts
Scripts for interacting with OpenStack
==========
Manage:
* instances
* cinder blocks
* torque cluster

==========
### swift_loader.py
Stage files from remote server into cinder block before uploading into swift

Requires a config.json:
```json
{
	"remote-ip" : "192.170.228.3",
	"remote-user" : "JGRUNDSTAD",
	"remote-dir" : "/glusterfs/netapp/homes1/whitelab-pancreatic/sequences/PANCAN",
	"project" : "PANCAN"
}
```
Usage:
`cat filename_list.txt | \
xargs -P <threads> -n 1 -IFILE python swift_loader.py -j config.json -f FILE`
* Downloads `FILE` from `remote-user@remote-ip:remote-dir`.
* Load `FILE` into the `project` swift container in 1GB chunks.
* Deletes `FILE` from staging area.

TODO: Error checking, exception handling


