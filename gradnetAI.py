import boto3

client = boto3.client('s3')
paginator = client.get_paginator('list_objects_v2')

response_iterator = paginator.paginate(
    Bucket='grandnet',
    Prefix='test/'
)
list = []

for page in response_iterator:
    for content in page['Contents']:
        list.append(content['Key'])

for i in range(1,len(list)):
    file_path = './input/'+list[i][5:]
    bucket = 'grandnet'
    key = list[i]

    client = boto3.client('s3')
    client.download_file(bucket, key, file_path)