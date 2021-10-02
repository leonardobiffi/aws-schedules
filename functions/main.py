import os, json
from datetime import datetime, timedelta
from logger.main import *

# Debug if enable
debugmode = os.getenv('DEBUG', False)

def debugout(module, data):
    if debugmode:
        logger.info("DEBUG %s : %s" % (module, data))

def flattenjson(b, delim):
    val = {}
    for i in b.keys():
        if isinstance( b[i], dict ):
            get = flattenjson( b[i], delim )
            for j in get.keys():
                val[ i + delim + j ] = get[j]
        else:
            val[i] = b[i]

    return val

def dict_to_string(d):
    val = ""
    for k, v in d.items():
         if type(v) is list:
             vs='/'.join(str(s) for s in v)
         else:
             vs=v
         if len(val) == 0 :
             val=k+"="+str(vs)
         else:
             val=val+" "+k+"="+str(vs)

    return val

# state = start | stop
def checkdate(data, state: str, day: str, hh: str):
    debugout('checkdate', "DEBUG checkdate state (%s) day (%s) hh (%s) data (%s)" % (state, day, hh, data))

    try:
        schedule = {}
        if data == '':
            debugout('checkdate', "data is empty")
            return False
        elif len(data) > 1 and data[0] == '{':
            # JSON-Format
            debugout('checkdate', 'JSON format found. (%s)' % data)
            schedule = json.loads(data)
        else:
            # RDS-Format
            try:

                debugout('checkdate', "RDS format found")
                # remove ' ' at atart and end, replace multiple ' ' with ' '
                t=dict(x.split('=') for x in ' '.join(data.split()).split(' '))
                for d in t.keys():
                    dday, datastate=d.split('_')
                    val=[int(i) for i in t[d].split('/')]
                    debugout('checkdate', "RDS data: dday (%s) datastate (%s) val (%s)" %(dday, datastate, val))
                    dstate={}
                    dstate[datastate]=val
                    if dday in schedule:
                        schedule[dday].update(dstate)
                    else:
                        schedule[dday]=dstate

            except Exception as e:
                logger.error("Error checkdate : %s" % (e))

        if debugout:
            for d in schedule.keys():
                for s in schedule[d].keys():
                    debugout('checkdate', 'keys: day (%s) state (%s)' % (d, s))

    except:
        logger.error("Error checkdate invalid data : %s : %s" % (data, e))

    try:
        schedule_data = []

        if day in schedule.keys() and state in schedule[day]:
            if type(schedule[day][state]) is list:
                schedule_data = schedule[day][state]
            else:
                schedule_data = [schedule[day][state]]
            debugout('checkdate', 'day schedule_data %s' % ', '.join(str(s) for s in schedule_data))

        if 'daily' in schedule.keys() and state in schedule['daily']:
            if type(schedule['daily'][state]) is list:
                schedule_data.extend(schedule['daily'][state])
            else:
                schedule_data.extend([int(schedule['daily'][state])])
            debugout('checkdate', 'daily schedule_data %s' % ', '.join(str(s) for s in schedule_data))

        workdays = ['mon', 'tue', 'wed', 'thu', 'fri']
        if day in workdays and 'workday' in schedule.keys() and state in schedule['workday']:
            debugout('checkdate', 'workday found')
            if type(schedule['workday'][state]) is list:
                schedule_data.extend(schedule['workday'][state])
            else:
                schedule_data.extend([schedule['workday'][state]])
            debugout('checkdate', 'workday schedule_data %s' % ', '.join(str(s) for s in schedule_data))

        debugout('checkdate', 'len %i schedule_data %s' % (len(schedule_data), ','.join(str(s) for s in schedule_data)))

        if int(hh) in schedule_data:
            logger.info("checkdate %s time matches hh (%i)" % (state, int(hh)))
            return True

        return False
    except Exception as e:
        logger.error("Error checkdate %s time : %s" % (state, e))

def check_desiredcount_tag(data, state, day, hh):
    debugout('check_desiredcount', "DEBUG check_desiredcount state (%s) day (%s) hh (%s) data (%s)" % (state, day, hh, data))

    try:
        schedule = {}
        if data == '':
            debugout('check_desiredcount', "data is empty")
            return False
        else:
            # ECS-Format
            try:
                debugout('check_desiredcount', "ECS format found")
                # remove ' ' at atart and end, replace multiple ' ' with ' '
                t=dict(x.split('=') for x in ' '.join(data.split()).split(' '))
                for d in t.keys():
                    dday, datastate=d.split('_')
                    val=[int(i) for i in t[d].split('/')]
                    debugout('check_desiredcount', "ECS data: dday (%s) datastate (%s) val (%s)" %(dday, datastate, val))
                    dstate={}
                    dstate[datastate]=val
                    if dday in schedule:
                        schedule[dday].update(dstate)
                    else:
                        schedule[dday]=dstate

            except Exception as e:
                logger.error("Error check_desiredcount : %s" % (e))

        if debugout:
            for d in schedule.keys():
                for s in schedule[d].keys():
                    debugout('check_desiredcount', 'keys: day (%s) state (%s)' % (d, s))

    except:
        logger.error("Error check_desiredcount invalid data : %s : %s" % (data, e))

    try:
        schedule_data = []

        if day in schedule.keys() and state in schedule[day]:
            if type(schedule[day][state]) is list:
                schedule_data = schedule[day][state]
            else:
                schedule_data = [schedule[day][state]]
            debugout('check_desiredcount', 'day schedule_data %s' % ', '.join(str(s) for s in schedule_data))

        if 'daily' in schedule.keys() and state in schedule['daily']:
            if type(schedule['daily'][state]) is list:
                schedule_data.extend(schedule['daily'][state])
            else:
                schedule_data.extend([int(schedule['daily'][state])])
            debugout('check_desiredcount', 'daily schedule_data %s' % ', '.join(str(s) for s in schedule_data))

        workdays = ['mon', 'tue', 'wed', 'thu', 'fri']
        if day in workdays and 'workday' in schedule.keys() and state in schedule['workday']:
            debugout('check_desiredcount', 'workday found')
            if type(schedule['workday'][state]) is list:
                schedule_data.extend(schedule['workday'][state])
            else:
                schedule_data.extend([schedule['workday'][state]])
            debugout('check_desiredcount', 'workday schedule_data %s' % ', '.join(str(s) for s in schedule_data))

        debugout('check_desiredcount', 'len %i schedule_data %s' % (len(schedule_data), ','.join(str(s) for s in schedule_data)))

        return schedule_data

    except Exception as e:
        logger.error("Error check_desiredcount %s time : %s" % (state, e))


def check_service_desiredcount(dynamodb_client, service, desiredCount):
    try:
        get_item = dynamodb_client.get_item(
            TableName='ecs-schedule',
            Key={
                'service': {
                    'S': service
                }
            }
        )

        return True

    except Exception as e:
        # Add desiredCount if Not Found
        update_table = dynamodb_client.put_item(
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