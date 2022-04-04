"""An AWS Python Pulumi program"""

import base64

import pulumi_aws as aws
import pulumi_command as command
from pulumi import Config, ResourceOptions, export

# create a SSH keypair to connect to instance
# ssh-keygen -t rsa -f rsa -m PEM

# cat .ssh/rsa | pulumi config set privateKey --secret --
# cat .ssh/rsa.pub | pulumi config set public_key

# https://www.pulumi.com/docs/intro/concepts/secrets/
config = Config()
keyname = config.get('Keyname')
public_key = config.get('public_key')

# The privateKey associated with the selected key must be provided (either directly or base64 encoded)
def decode_key(key):
    try:
        key = base64.b64decode(key.encode('ascii')).decode('ascii')
    except:
        pass
    if key.startswith('-----BEGIN RSA PRIVATE KEY-----'):
        return key
    return key.encode('ascii')

private_key = config.require_secret('privateKey').apply(decode_key)

if keyname is None: 
    key = aws.ec2.KeyPair('pulumi_key', public_key=public_key)
    keyname = key.key_name
    

# https://docs.aws.amazon.com/efs/latest/ug/network-access.html
sg = aws.ec2.SecurityGroup("name",
                           description="Allow inbound SSH and postgres connections",
                           ingress=[aws.ec2.SecurityGroupIngressArgs(
                               protocol="tcp",
                               from_port=22,
                               to_port=22,
                               cidr_blocks=["0.0.0.0/0"],
                           ),
                           aws.ec2.SecurityGroupIngressArgs(
                               protocol="tcp",
                               from_port=5432,
                               to_port=5432,
                               cidr_blocks=["0.0.0.0/0"],
                           )])

timescaledb_ami = aws.ec2.get_ami(
    filters=[
        aws.ec2.GetAmiFilterArgs(
            name="name",
            values=["TimescaleDB*"],
        ),
        aws.ec2.GetAmiFilterArgs(
            name="virtualization-type",
            values=["hvm"],
        ),
    ],
    owners=["142548018081"],
    most_recent=True)

ec2_instance = aws.ec2.Instance(
    "ec2-timescaledb",
    ami=timescaledb_ami.id,
    instance_type="t2.micro",
    vpc_security_group_ids=[sg.id],
    user_data="""
    #!/bin/bash
    sudo chmod 644 /etc/postgresql/13/main/postgresql.conf
    """,
    key_name=keyname,
)

#https://www.pulumi.com/blog/architecture-as-code-vm/
connection = command.remote.ConnectionArgs(
    host=ec2_instance.public_ip,
    user='ubuntu',
    private_key=private_key,
)

cp_config = command.remote.CopyFile('config',
    connection=connection,
    local_path='./postgres/postgres.conf',
    remote_path='./postgres.conf',
    opts=ResourceOptions(depends_on=[ec2_instance]),
)

cp_config = command.remote.CopyFile('config2',
    connection=connection,
    local_path='./postgres/pg_hba.conf',
    remote_path='./pg_hba.conf',
    opts=ResourceOptions(depends_on=[ec2_instance]),
)

cp_config = command.remote.CopyFile('config3',
    connection=connection,
    local_path='./postgres/postgres_setup.sh',
    remote_path='./postgres_setup.sh',
    opts=ResourceOptions(depends_on=[ec2_instance]),
)

cp_config2 = command.remote.CopyFile('sqlfile',
    connection=connection,
    local_path='./sqlcommands.sql',
    remote_path='./sqlcommands.sql',
    opts=ResourceOptions(depends_on=[ec2_instance]),
)

# Execute a basic command on our server.
cat_config = command.remote.Command('timescaledb-config',
    connection=connection,
    create='sudo chmod 755 postgres_setup.sh && ./postgres_setup.sh',
    opts=ResourceOptions(depends_on=[cp_config])
)

export("ip", ec2_instance.public_ip)
export("hostname", ec2_instance.public_dns)


