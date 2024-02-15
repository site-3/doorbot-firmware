# Site 3 Doorbot Tester mk2
#


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



def local_test_auth(tag):
    controller.log_file = "rpi/test_files/test_logs.txt"
    members = controller.Members(filename="rpi/test_files/testMembers.csv")
    roles = controller.Roles(filename="rpi/test_files/testRoles.csv")
    ok, reason = controller.test_auth(wiegandify(tag), members, roles)
    return ok, reason