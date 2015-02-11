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
`python swift_loader.py -j config.json -f <FILE>`
* Downloads `FILE` from `remote-user@remote-ip:remote-dir`
* load `FILE` into the `project` swift container in 1GB chunks
* deletes `FILE` from staging area


