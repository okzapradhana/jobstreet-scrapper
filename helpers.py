import timeago
from dateutil import parser
from datetime import datetime
from pytz import timezone
from config import TIMEZONE

def time_difference_fmt(posted_time):
    tz_jakarta = timezone(TIMEZONE)
    now = datetime.now(tz=tz_jakarta)
    job_post_time = parser.parse(posted_time) # convert ISO 8601 time to Datetime Object
    job_post_time = job_post_time.astimezone(tz=tz_jakarta) # convert UTC Datetime to GMT+7 Timezone

    return timeago.format(job_post_time, now)
