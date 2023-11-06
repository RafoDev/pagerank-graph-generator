import boto3

s3 = boto3.resource('s3')
bucket_name = 'search-engine-bd'

bucket = s3.Bucket(bucket_name)

bucket.objects.all().delete()