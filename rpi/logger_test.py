from datetime import (datetime, timedelta)
import os
import pytest

import logger

def test_logging():
    logger.log_folder="rpi/test_files/test_logs/"
    msg = "test1"
    #first we should cleanup that log folder.
    l = logger.Logger()
    now = datetime.now().__sub__(timedelta(days=365*30)) #this is so that you wont accidentally have a present day test log.

    #if the log already exists, we remove it to test from a clean slate
    if os.path.exists(l.get_log_file_str(now)):
        os.remove(l.get_log_file_str(now))

    l.log(msg, when=now, verbose=0)#this is an item that should always be logged

    f = open(l.get_log_file_str(now))
    lines = f.readlines()
    f.close

    assert len(lines)==1 #should just have the one log.
    line = lines[0]
    assert line.split(":>")[-1] == "{}\n".format(msg)#test the end string is correct (with an added newline)



# test that the files are stored in the correct slot.
def test_log_file_str():
    logger.log_folder = "folder/"
    log_file = logger.Logger().get_log_file_str(datetime(year=1924, month=1, day=2),mk_log_dr=False)
    assert log_file == "folder/1924/log_1_2.txt"
