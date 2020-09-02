"""
script used to assist the metrics scripts by using sleep
"""

import datetime
import time


def reset_sleep(auth):
    """
    function that sleeps for a given time to await the next rate-limit reset
    :param auth: auth object to access the rate-limits
    :return: False
    """
    try:
        waiting_sec = int((auth.get_rate_limit().core.reset - datetime.datetime.utcnow()).total_seconds()) + 1
        local_reset_time = datetime.datetime.fromtimestamp(float(auth.get_rate_limit().core.reset.strftime("%s")),
                                                           datetime.datetime.now().astimezone().tzinfo)

        print('OSCTool waits', waiting_sec, 'seconds for the next rate-limit reset and will be done at around',
              local_reset_time)
        time.sleep(waiting_sec)
    except Exception as e:
        print(str(e))
        print('Please make sure your time is set correct on your local machine '
              '(timezone does not matter) and run the script again')
        quit()
