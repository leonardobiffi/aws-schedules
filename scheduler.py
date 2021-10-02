import boto3
import os, datetime, time, pytz

from logger.main import *
from functions.main import *
from functions.telegram import *
from functions.time import *

aws_region = None

rds_schedule = os.getenv('RDS_SCHEDULE', 'True')
rds_schedule = rds_schedule.capitalize()
logger.info("rds_schedule is %s" % rds_schedule)

ec2_schedule = os.getenv('EC2_SCHEDULE', 'True')
ec2_schedule = ec2_schedule.capitalize()
logger.info("ec2_schedule is %s" % ec2_schedule)

ecs_schedule = os.getenv('ECS_SCHEDULE', 'True')
ecs_schedule = ecs_schedule.capitalize()
logger.info("ecs_schedule is %s" % ecs_schedule)

telegram_alert = os.getenv('TELEGRAM_ALERT', 'False')
logger.info("telegram alert is %s" % ecs_schedule)

#
# Init EC2
#
def ec2_init():
    # Setup AWS connection
    aws_region = os.getenv('REGION', 'us-east-1')

    global ec2
    logger.info("Connecting to region \"%s\"", aws_region)
    ec2 = boto3.resource('ec2', region_name=aws_region)
    logger.info("Connected to region \"%s\"", aws_region)

#
# Loop EC2 instances and check if a 'schedule' tag has been set. Next, evaluate value and start/stop instance if needed.
#
def ec2_check(event):
    # Get all reservations.
    instances = ec2.instances.filter(
    Filters=[{'Name': 'instance-state-name', 'Values': ['pending','running','stopping','stopped']}])

    # Get current day + hour
    day, hh = get_day_hh(event, "ec2")
    
    started = []
    stopped = []

    schedule_tag = os.getenv('TAG', 'schedule')
    logger.info("Schedule tag is called \"%s\"", schedule_tag)
    if not instances:
        logger.error('Unable to find any EC2 Instances, please check configuration')
    
    for instance in instances:
        logger.info("Evaluating EC2 instance \"%s\" state %s" % (instance.id, instance.state["Name"]))

        try:
            data = "{}"
            for tag in instance.tags:
                if schedule_tag in tag['Key']:
                    data = tag['Value']
                    break
            else:
                logger.info("Not found Tag Name: \"%s\", skipping ..." %(schedule_tag))
            
            # Start instances
            try:
                if checkdate(data, 'start', day, hh) and instance.state["Name"] != 'running':

                    logger.info("Starting EC2 instance \"%s\" ..." %(instance.id))
                    started.append(instance.id)
                    ec2.instances.filter(InstanceIds=[instance.id]).start()
            except Exception as e:
                logger.error("Error checking start time : %s" % e)
                pass

            # Stop instances
            try:
                if checkdate(data, 'stop', day, hh) and instance.state["Name"] == 'running':

                    logger.info("Stopping EC2 instance \"%s\" ..." %(instance.id))
                    stopped.append(instance.id)
                    ec2.instances.filter(InstanceIds=[instance.id]).stop()
            except Exception as e:
                logger.error("Error checking stop time : %s" % e)

        except ValueError as e:
            # invalid JSON
            logger.error('Invalid value for tag \"schedule\" on EC2 instance \"%s\", please check!' %(instance.id))

    if telegram_alert == 'True':
        alarm_ec2(started, stopped)


def rds_init():
    # Setup AWS connection
    aws_region = os.getenv('REGION', 'us-east-1')

    logger.info("Connecting rds to region \"%s\"", aws_region)
    global rds
    rds = boto3.client('rds', region_name=aws_region)
    logger.info("Connected rds to region \"%s\"", aws_region)

#
# Loop RDS instances and check if a 'schedule' tag has been set. Next, evaluate value and start/stop instance if needed.
#
def rds_check(event):
    # Get all reservations.
    instances = rds.describe_db_instances()
    clusters = rds.describe_db_clusters()

    # Get current day + hour
    day, hh = get_day_hh(event, "rds")

    if not instances:
        logger.error('Unable to find any RDS Instances, please check configuration')
    
    rds_loop(instances, hh, day, 'Instance')
    rds_loop(clusters, hh, day, 'Cluster')


#
# Checks the schedule tags for instances or clusters, and stop/starts accordingly
#
def rds_loop(rds_objects, hh, day, object_type):
    started = []
    stopped = []

    schedule_tag = os.getenv('TAG', 'schedule')
    logger.info("schedule tag is called \"%s\"", schedule_tag)
    
    for instance in rds_objects['DB'+object_type+'s']:
        if 'DBInstanceStatus' not in instance: instance['DBInstanceStatus'] = ''
        if 'Status' not in instance: instance['Status'] = ''
        # instance = json.loads(db_instance)
        
        logger.info("Evaluating RDS instance \"%s\" state: %s" % (instance['DB'+object_type+'Identifier'], instance['DBInstanceStatus']))
        response = rds.list_tags_for_resource(ResourceName=instance['DB'+object_type+'Arn'])
        taglist = response['TagList']
        
        try:
            data = ""
            for tag in taglist:
                if schedule_tag in tag['Key']:
                    data = tag['Value']
                    break
            else:
                logger.info("Not found Tag Name: \"%s\", skipping ..." %(schedule_tag))

            try:
                # Convert the start/stop hour into a list, in case of multiple values
                if checkdate(data, 'start', day, hh) and (instance['DBInstanceStatus'] == 'stopped' or instance['Status'] == 'stopped'):

                    logger.info("Starting RDS instance \"%s\"." %(instance['DB'+object_type+'Identifier']))
                    started.append(instance['DB'+object_type+'Identifier'])
                    
                    if object_type == 'Instance': rds.start_db_instance(DBInstanceIdentifier=instance['DB'+object_type+'Identifier'])
                    if object_type == 'Cluster': rds.start_db_cluster(DBClusterIdentifier=instance['DB'+object_type+'Identifier'])

                elif checkdate(data, 'stop', day, hh) and (instance['DBInstanceStatus'] == 'available' or instance['Status'] == 'available'):
                    
                    logger.info("Stopping RDS instance \"%s\"." %(instance['DB'+object_type+'Identifier']))
                    stopped.append(instance['DB'+object_type+'Identifier'])
                    
                    if object_type == 'Instance': rds.stop_db_instance(DBInstanceIdentifier=instance['DB'+object_type+'Identifier'])
                    if object_type == 'Cluster': rds.stop_db_cluster(DBClusterIdentifier=instance['DB'+object_type+'Identifier'])
            
            except Exception as e:
                logger.info("ERROR rds_loop \"%s\" " % (e))
                pass # catch exception if 'stop' is not in schedule.

        except ValueError as e:
            # invalid JSON
            logger.error(e)
            logger.error('Invalid value for tag \"schedule\" on RDS instance \"%s\", please check!' %(instance['DB'+object_type+'Identifier']))
    
    if telegram_alert == 'True':
        alarm_rds(started, stopped)

def ecs_init():
    # Setup AWS connection
    aws_region = os.getenv('REGION', 'us-east-1')
    logger.info("Connecting ecs to region \"%s\"", aws_region)
    
    global ecs, dynamodb_client, autoscaling
    ecs = boto3.client('ecs', region_name=aws_region)
    autoscaling = boto3.client("application-autoscaling", region_name=aws_region)
    dynamodb_client = boto3.client('dynamodb', region_name=aws_region)

    logger.info("Connected ecs to region \"%s\"", aws_region)

def ecs_check(event):
    # Get all Clusters
    clusters = ecs.list_clusters()

    started = []
    stopped = []

    schedule_tag = os.getenv('TAG', 'schedule')
    logger.info("schedule tag is called \"%s\"", schedule_tag)

    # Get current day + hour
    day, hh = get_day_hh(event, "ecs")

    for cluster in clusters['clusterArns']:
        response_tags = ecs.list_tags_for_resource(resourceArn=cluster)
        tags_list = response_tags['tags']

        services = ecs.list_services(
            cluster=cluster
        )

        cluster_details = ecs.describe_clusters(
            clusters=[cluster]
        )

        cluster_name = cluster_details["clusters"][0]["clusterName"]

        logger.info('Cluster: {}'.format(cluster_name))

        data = "{}"
        for tag in tags_list:
            if schedule_tag in tag['key']:
                data = tag['value']
                break
        else:
            logger.info("Not found Tag Name: \"%s\", skipping ..." %(schedule_tag))

        for service in services['serviceArns']:
            service_details = ecs.describe_services(
                cluster=cluster,
                services=[service]
            )

            service_name = service_details["services"][0]["serviceName"]

            logger.info("Checking service: {}".format(service_name))

            # Get MaxCapacity
            response = autoscaling.describe_scalable_targets(
                ServiceNamespace='ecs',
                ResourceIds=[
                    "service/{}/{}".format(cluster_name, service_name),
                ],
                ScalableDimension='ecs:service:DesiredCount'
            )

            desired_count = int(service_details['services'][0]['desiredCount'])
            max_capacity = response["ScalableTargets"][0]["MaxCapacity"]

            # Start Tasks
            try:
                if checkdate(data, 'start', day, hh) and check_service_desiredcount( dynamodb_client ,service, desired_count):
                    # Get desired count stored in dynamodb table
                    get_item = dynamodb_client.get_item(
                        TableName='ecs-schedule',
                        Key={
                            'service': {
                                'S': service
                            }
                        }
                    )

                    desired_count = get_item['Item']['desired_count']['N']
                    max_capacity_default = get_item['Item']['max_capacity']['N']
                    
                    logger.info("Update to default {} Tasks in Service {}".format(desired_count, service_name))

                    # Update service desiredCount
                    update_service = ecs.update_service(
                        cluster=cluster,
                        service=service,
                        desiredCount=int(desired_count)
                    )

                    # Update Autoscaling Min to desiredCount
                    update_autoscaling = autoscaling.register_scalable_target(
                        ServiceNamespace="ecs",
                        ResourceId="service/{}/{}".format(cluster_name, service_name),
                        ScalableDimension="ecs:service:DesiredCount",
                        MinCapacity=int(desired_count),
                        MaxCapacity=int(max_capacity_default)
                    )

                    started.append(service_name)

            except Exception as e:
                logger.info("Error checking start time : %s" % e)
                pass                

            # Stop Tasks
            try:
                if checkdate(data, 'stop', day, hh) and check_service_desiredcount( dynamodb_client ,service, desired_count):
                    
                    tag_desiredcount = check_desiredcount_tag(data, 'stop-desired', day, hh)
                    if len(tag_desiredcount) == 0:
                        # set to 0, stop all
                        tag_desiredcount = 0
                    else:
                        # get first indice
                        tag_desiredcount = tag_desiredcount[0]
                    
                    logger.info("Update to {} Tasks in Service {}".format(tag_desiredcount, service_name))

                    # Update default desiredCount
                    update_table = dynamodb_client.put_item(
                        TableName='ecs-schedule',
                        Item={
                            'service': {
                                'S': service
                            },
                            'desired_count': {
                                'N': str(desired_count)
                            },
                            'max_capacity': {
                                'N': str(max_capacity)
                            }
                        }
                    )

                    # Update service desiredCount
                    update_service = ecs.update_service(
                        cluster=cluster,
                        service=service,
                        desiredCount=int(tag_desiredcount)
                    )

                    # Update Autoscaling Min to desiredCount
                    update_autoscaling = autoscaling.register_scalable_target(
                        ServiceNamespace="ecs",
                        ResourceId="service/{}/{}".format(cluster_name, service_name),
                        ScalableDimension="ecs:service:DesiredCount",
                        MinCapacity=int(tag_desiredcount),
                        MaxCapacity=int(tag_desiredcount)
                    )

                    stopped.append(service_name)
                    
            except Exception as e:
                logger.info("Error checking stop time : %s" % e)
    
    if telegram_alert == 'True':
        alarm_ecs(started, stopped)

# Main function. Entrypoint for Lambda
def handler(event, context):

    if (ec2_schedule == 'True'):
        ec2_init()
        ec2_check(event)

    if (rds_schedule == 'True'):
        rds_init()
        rds_check(event)
    
    if (ecs_schedule == 'True'):
        ecs_init()
        ecs_check(event)

# Manual invocation of the script (only used for testing)
if __name__ == "__main__":
    # Test data
    test = {}
    handler(test, None)
