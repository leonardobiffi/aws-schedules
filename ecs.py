import boto3

ecs = boto3.client('ecs')
dyn = boto3.client('dynamodb')

def disable_tasks(service, desired_count):
    update_table = dyn.put_item(
        TableName='ecs-schedule',
        Item={
            'service': {
                'S': service
            },
            'desired_count': {
                'N': str(desired_count)
            }
        }
    )

    #update_service = ecs.update_service(
    #    cluster=cluster,
    #    service=service,
    #    desiredCount=0
    #)

def enable_tasks():


def main():
    clusters = ecs.list_clusters()

    for cluster in clusters['clusterArns']:

        services = ecs.list_services(
            cluster=cluster
        )

        print('Cluster: {}'.format(cluster))

        for service in services['serviceArns']:
            print("Update service: {}".format(service))

            service_details = ecs.describe_services(
                cluster=cluster,
                services=[service]
            )

            desired_count = service_details['services'][0]['desiredCount']

            disable_tasks(service, desired_count)

        break

main()