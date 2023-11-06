import boto3

s3_client = boto3.client('s3')
bucket_name = 'search-engine-bd'

object_key = 'mi_carpeta'

contenido_del_archivo = 'Este es el contenido de mi archivo.'

s3_client.put_object(Bucket=bucket_name, Key='data')
s3_client.put_object(Bucket=bucket_name, Key='corpus')
s3_client.put_object(Bucket=bucket_name, Key='corpus/pdf')
s3_client.put_object(Bucket=bucket_name, Key='corpus/txt')