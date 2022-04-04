Running the Example
First, create a stack, using pulumi stack init.

Next, generate an OpenSSH keypair for use with your server - as per the AWS Requirements

$ ssh-keygen -t rsa -f rsa -b 4096 -m PEM
This will output two files, rsa and rsa.pub, in the current directory. Be sure not to commit these files!

We then need to configure our stack so that the public key is used by our EC2 instance, and the private key used for subsequent SCP and SSH steps that will configure our server after it is stood up.

$ cat rsa.pub | pulumi config set publicKey --
$ cat rsa | pulumi config set privateKey --secret --
Notice that we've used --secret for privateKey. This ensures their are stored in encrypted form in the Pulumi secrets system.

Also set your desired AWS region:

$ pulumi config set aws:region us-west-2

From there, you can run pulumi up and all resources will be provisioned and configured.