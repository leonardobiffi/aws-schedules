import boto3
import sys, os, json, logging, datetime, time, pytz

def check_service_desiredcount(service, desiredCount):
    try:
        get_item = dyn.get_item(
            TableName='ecs-schedule',
            Key={
                'service': {
                    'S': service
                }
            }
        )

        if int(get_item['Item']['desired_count']['N']) == int(desiredCount):
            return True
        else:
            return False

    except Exception as e:
        # Add desiredCount if Not Found
        update_table = dyn.put_item(
            TableName='ecs-schedule',
            Item={
                'service': {
                    'S': service
                },
                'desired_count': {
                    'N': str(desiredCount)
                }
            }
        )

        return True

ecs = boto3.client('ecs', region_name='us-east-1')
dyn = boto3.client('dynamodb', region_name='us-east-1')

schedule_tag = os.getenv('TAG', 'schedule')
cluster = 'arn:aws:ecs:us-east-1:164625275729:cluster/99-api'

response_tags = ecs.list_tags_for_resource(resourceArn=cluster)

tags_list = response_tags['tags']
data = "{}"

for tag in tags_list:
    if schedule_tag in tag['key']:
        data = tag['value']
        break
else:
    print("Not found Tag Name: \"%s\", skipping ..." %(schedule_tag))

services = ecs.list_services(
    cluster=cluster
)

print('Cluster: {}'.format(cluster))

for service in services['serviceArns']:
    print("Updating service: {}".format(service))

    service_details = ecs.describe_services(
        cluster=cluster,
        services=[service]
    )

    desiredCount = service_details['services'][0]['desiredCount']
    print("Desired Count: {}".format(desiredCount))

    if check_service_desiredcount(service, desiredCount):
        print("Nothing to change")
    else:
        print("Set Desired {}".format(desiredCount))