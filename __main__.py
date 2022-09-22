"""An AWS Python Pulumi program"""
import os

from pulumi import export, FileAsset
from pulumi_aws import s3
import mimetypes



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
export('bucket_name', bucket.website_endpoint)