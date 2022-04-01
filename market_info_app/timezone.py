from datetime import datetime
import pytz

def is_dst():
    """Determine whether or not Daylight Savings Time (DST)
    is currently in effect"""

    x = datetime(datetime.now().year, 1, 1, 0, 0, 0, tzinfo=pytz.timezone('US/Eastern')) # Jan 1 of this year
    y = datetime.now(pytz.timezone('US/Eastern'))

    # if DST in effect, offset will be different
    return (y.utcoffset() != x.utcoffset())

if __name__ == "__main__":
    print(is_dst())
