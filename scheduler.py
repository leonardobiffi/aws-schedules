import boto3
import sys, os, json, logging, datetime, time, pytz

from logger.main import *
from functions.main import *

aws_region = None

create_schedule_tag_force = os.getenv('SCHEDULE_TAG_FORCE', 'False')
create_schedule_tag_force = create_schedule_tag_force.capitalize()
logger.info("create_schedule_tag_force is %s" % create_schedule_tag_force)

rds_schedule = os.getenv('RDS_SCHEDULE', 'True')
rds_schedule = rds_schedule.capitalize()
logger.info("rds_schedule is %s" % rds_schedule)

ec2_schedule = os.getenv('EC2_SCHEDULE', 'True')
ec2_schedule = ec2_schedule.capitalize()
logger.info("ec2_schedule is %s" % ec2_schedule)

#
# Init EC2
#
def ec2_init():
    # Setup AWS connection
    aws_region = os.getenv('AWS_REGION', 'us-east-1')

    global ec2
    logger.info("Connecting to region \"%s\"", aws_region)
    ec2 = boto3.resource('ec2', region_name=aws_region)
    logger.info("Connected to region \"%s\"", aws_region)

#
# Loop EC2 instances and check if a 'schedule' tag has been set. Next, evaluate value and start/stop instance if needed.
#
def ec2_check():
    # Get all reservations.
    instances = ec2.instances.filter(
    Filters=[{'Name': 'instance-state-name', 'Values': ['pending','running','stopping','stopped']}])

    # Get current day + hour (using gmt by default if time parameter not set to local)
    time_zone =  os.getenv('TIME', 'gmt')
    if time_zone == 'local':
        hh  = int(time.strftime("%H", time.localtime()))
        day = time.strftime("%a", time.localtime()).lower()
        logger.info("Checking for EC2 instances to start or stop for 'day' " + day + " 'local time' hour " + str(hh))
    elif time_zone == 'gmt':
        hh  = int(time.strftime("%H", time.gmtime()))
        day = time.strftime("%a", time.gmtime()).lower()
        logger.info("Checking for EC2 instances to start or stop for 'day' " + day + " 'gmt' hour " + str(hh))
    else:
        if time_zone in pytz.all_timezones:
            d = datetime.datetime.now()
            d = pytz.utc.localize(d)
            req_timezone = pytz.timezone(time_zone)
            d_req_timezone = d.astimezone(req_timezone)
            hh = int(d_req_timezone.strftime("%H"))
            day = d_req_timezone.strftime("%a").lower()
            logger.info("Checking for EC2 instances to start or stop for 'day' " + day + " '" + time_zone + "' hour " + str(hh))
        else:
            logger.error('Invalid time timezone string value \"%s\", please check!' %(time_zone))
            raise ValueError('Invalid time timezone string value')
    
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
            
            # Start instances
            try:
                if checkdate(data, 'start', day, hh) and instance.state["Name"] != 'running':

                    logger.info("Starting EC2 instance \"%s\" ..." %(instance.id))
                    started.append(instance.id)
                    #ec2.instances.filter(InstanceIds=[instance.id]).start()
            except Exception as e:
                logger.error("Error checking start time : %s" % e)
                pass

            # Stop instances
            try:
                if checkdate(data, 'stop', day, hh) and instance.state["Name"] == 'running':

                    logger.info("Stopping EC2 instance \"%s\" ..." %(instance.id))
                    stopped.append(instance.id)
                    #ec2.instances.filter(InstanceIds=[instance.id]).stop()
            except Exception as e:
                logger.error("Error checking stop time : %s" % e)

        except ValueError as e:
            # invalid JSON
            logger.error('Invalid value for tag \"schedule\" on EC2 instance \"%s\", please check!' %(instance.id))


# Main function. Entrypoint for Lambda
def handler(event, context):

    if (ec2_schedule == 'True'):
        ec2_init()
        ec2_check()

    #if (rds_schedule == 'True'):
    #    rds_init()
    #    rds_check()

# Manual invocation of the script (only used for testing)
if __name__ == "__main__":
    # Test data
    test = {}
    handler(test, None)
