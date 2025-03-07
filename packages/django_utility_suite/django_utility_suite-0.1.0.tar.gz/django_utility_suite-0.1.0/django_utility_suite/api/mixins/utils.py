import datetime


def seconds_until(target_hour, target_minute=0, target_second=0):
    now = datetime.datetime.now()
    target = now.replace(
        hour=target_hour,
        minute=target_minute,
        second=target_second,
        microsecond=0,
    )

    if target <= now:
        target += datetime.timedelta(days=1)

    return int((target - now).total_seconds())
