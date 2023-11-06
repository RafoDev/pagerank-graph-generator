import boto3

s3_client = boto3.client('s3')
bucket_name = 'search-engine-bd'
s3_client.put_object(Bucket=bucket_name, Key='data/')

s3_client.put_object(Bucket=bucket_name, Key='inverted-index/output')
s3_client.put_object(Bucket=bucket_name, Key='inverted-index/result')

s3_client.put_object(Bucket=bucket_name, Key='page-rank/output/')
s3_client.put_object(Bucket=bucket_name, Key='page-rank/partials1/')
s3_client.put_object(Bucket=bucket_name, Key='page-rank/partials2/')
s3_client.put_object(Bucket=bucket_name, Key='page-rank/result/')
s3_client.put_object(Bucket=bucket_name, Key='corpus/pdf/')
s3_client.put_object(Bucket=bucket_name, Key='corpus/txt/')