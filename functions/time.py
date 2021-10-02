import time, pytz
from datetime import datetime, timedelta
from logger.main import *

def get_day_hh(event: dict[str, dict[str, str]], resource: str) -> tuple[str, str]:
    """
    Get current day + hour (using gmt by default if time parameter not set)
    """
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
            d = hour_rounder(datetime.now())
            d = pytz.utc.localize(d)
            req_timezone = pytz.timezone(time_zone)
            d_req_timezone = d.astimezone(req_timezone)
            hh = int(d_req_timezone.strftime("%H"))
            day = d_req_timezone.strftime("%a").lower()
            logger.info("Checking for EC2 instances to start or stop for 'day' " + day + " '" + time_zone + "' hour " + str(hh))
        else:
            logger.error('Invalid time timezone string value \"%s\", please check!' %(time_zone))
            raise ValueError('Invalid time timezone string value')
    
    # Get manual hour informed in event
    if resource in event:
        if "hour" in event[resource]:
            hh = event[resource]["hour"]
        else:
            logger.info("Hour not found in manual event")

    return day, str(hh)

def hour_rounder(t: datetime):
    """
    Rounds to nearest hour by adding a timedelta hour if minute >= 30
    """
    return (t.replace(second=0, microsecond=0, minute=0, hour=t.hour)
               +timedelta(hours=t.minute//30))