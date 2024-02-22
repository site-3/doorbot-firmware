# Site 3 Doorbot Tester mk2
#

import datetime
from rpi import logger
import pytest

import controller
from controller import (
    wiegandify
)

def test_dud_fob():
    ok,reason = local_test_auth('00001234')#not a fob
    assert not ok
    assert reason == "Could not find member with tag {}.".format(wiegandify("00001234"))


def test_expired():
    ok,reason = local_test_auth("a1868fff")#JFK fob. Should be expired.
    assert not ok
    assert reason == 'their access expired on 1963-11-22 at 23:59:59'

def test_good():
    ok, reason = local_test_auth("a1868111")#jonah's fob. Should be good
    assert ok
    assert reason == 'access is always granted'

def test_intro_check_access():
    #the intro member, generated off of their fob
    introMember = controller.Members(filename="rpi/test_files/testMembers.csv").get_by_tag(wiegandify("ffffffff"))

    time = datetime.datetime(year=2020, month=1, day=6, hour=12)#monday, noon.
    ok, _ = local_test_member_at_time(introMember, time)
    assert not ok #should fail, as intro members cant get in on monday mornings.

    time = datetime.datetime(year=2020, month=1, day=6, hour=16, minute=2)#monday, 16:02.
    ok, _ = local_test_member_at_time(introMember, time)
    assert ok #should let intro in after 4pm

    time = datetime.datetime(year=2020, month=1, day=1, hour=16, minute=2)#wed, 16:02.
    ok, _ = local_test_member_at_time(introMember, time)
    assert not ok #should not let member in on wed

    time = datetime.datetime(year=2020, month=1, day=4, hour=16, minute=2)#sat, 16:02.
    ok, _ = local_test_member_at_time(introMember, time)
    assert ok #should let intro in on sat
    
def local_test_member_at_time(member, time):
    logger.log_folder="rpi/test_files/test_logs/"
    roles = controller.Roles(filename="rpi/test_files/testRoles.csv")
    ok, reason = controller.check_access(roles.rules[member['Plan']], time=time)
    return ok, reason


def local_test_auth(tag):
    logger.log_folder="rpi/test_files/test_logs/"
    log = logger.Logger(5)
    members = controller.Members(filename="rpi/test_files/testMembers.csv")
    roles = controller.Roles(filename="rpi/test_files/testRoles.csv")
    ok, reason = controller.test_auth(wiegandify(tag), log, members, roles)
    return ok, reason