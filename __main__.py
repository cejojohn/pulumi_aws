"""An AWS Python Pulumi program"""
import os
import mimetypes
from re import I
from warnings import filters

from pulumi import export, FileAsset
from pulumi_aws import s3
from pulumi_aws import ec2

# AMI image configuration
ec2_image_owner = ["099720109477"]
ec2_image_device_type = ["ebs"]
ec2_image_name_prefix = ["ubuntu-*"]
ec2_instance_size = "t2.micro"
ec2_instance_name = "aws-ec2-ubuntu"
ec2_keypair_name = "pulumi_test_key"
ec2_ssh_port = 212

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

export("Image found: ", my_ec2_ami.name)