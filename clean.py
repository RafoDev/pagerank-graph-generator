import boto3

s3 = boto3.resource('s3')
bucket_name = 'search-engine-bd'

bucket = s3.Bucket(bucket_name)

for obj in bucket.objects.filter(Prefix='/data'):
    obj.delete()

for obj in bucket.objects.filter(Prefix='/corpus/pdf'):
    obj.delete()

for obj in bucket.objects.filter(Prefix='/corpus/txt'):
    obj.delete()

for obj in bucket.objects.filter(Prefix='/corpus'):
    obj.delete()