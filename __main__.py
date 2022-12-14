"""An AWS Python Pulumi program"""
import os
import mimetypes

from pulumi import export, FileAsset
from pulumi_aws import s3
from pulumi_aws import ec2

# AMI image configuration
ec2_image_owner = ["099720109477"]
ec2_image_device_type = ["ebs"]
ec2_image_name_prefix = ["ubuntu-*"]
ec2_instance_size = "t2.micro"
ec2_instance_name = "aws-ec2-ubuntu"
ec2_keypair_name = "blackmamba"
ec2_ssh_port = 212
ec2_user_data = """#!/bin/bash
echo "test data" >> ~/user_data_generated_test
sed -i 's/^#\?Port 22$/Port 2212/'  /etc/ssh/sshd_config
#mkdir /etc/systemd/system/ssh.socket.d
#echo 'Port 2212' > /etc/systemd/system/ssh.socket.d/addresses.conf
systemctl restart ssh
"""

# Create S3 Bucket with page
bucket = s3.Bucket('my-bucket1', 
    acl="public-read",
    website=s3.BucketWebsiteArgs(index_document="index.html"),
    tags={
        "Environments": "Dev",
        "Name": "mybucket",
        },
    )

cwd = os.path.dirname(__file__)
content_file = "index.html"
file_fullpath = os.path.join(cwd, content_file)
mime_type, _ = mimetypes.guess_type(file_fullpath)

s3_obj = s3.BucketObject(content_file, 
    bucket=bucket.id,
    source=FileAsset(file_fullpath),
    content_type=mime_type,
    acl="public-read",
    )

# Export the name of the bucket
export("bucket_name", bucket.website_endpoint)


my_ec2_ami = ec2.get_ami(
        most_recent=True,
        owners=ec2_image_owner,
        filters=[
            ec2.GetAmiFilterArgs(
                name="name",
                values=ec2_image_name_prefix,
            ),
            ec2.GetAmiFilterArgs(
                name="root-device-type",
                values=ec2_image_device_type,
            ),
        ],
)

export("Image used: ", my_ec2_ami.name)

my_security_group = ec2.SecurityGroup(
    "mySecurityGroup",
    description="Allow SSH on port 2212",
    ingress=[ec2.SecurityGroupIngressArgs(
        from_port=2212,
        to_port=2212,
        cidr_blocks=["0.0.0.0/0"],
        ipv6_cidr_blocks=["::/0"],
        protocol="tcp",
        ),
        ec2.SecurityGroupIngressArgs(
        from_port=22,
        to_port=22,
        cidr_blocks=["0.0.0.0/0"],
        ipv6_cidr_blocks=["::/0"],
        protocol="tcp",
        ),
    ],
    egress=[ec2.SecurityGroupEgressArgs(
        from_port=0,
        to_port=0,
        protocol="-1",
        cidr_blocks=["0.0.0.0/0"],
        ipv6_cidr_blocks=["::/0"],
        ),
    ],
)

my_ec2_instance = ec2.Instance(
            ec2_instance_name,
            ami=my_ec2_ami.id,
            key_name=ec2_keypair_name,
            instance_type=ec2_instance_size,
            user_data=ec2_user_data,
            vpc_security_group_ids=[my_security_group.id],
            )

export("Instance IP: ", my_ec2_instance.public_ip)