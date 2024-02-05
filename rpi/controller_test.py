# Site 3 Doorbot Tester mk2
#


import pytest
import sys
import csv
import os.path
from controller import *
import controller

def test_dud_fob():
    ok,reason = local_test_auth('00001234')#not a fob
    assert not ok
    assert reason == "Could not find member with tag 00001234."


def test_expired():
    ok,reason = local_test_auth(wiegandify("a1868fff"))#JFK fob. Should be expired.
    assert not ok
    assert reason == 'their access expired on 1963-11-22 at 23:59:59'

def test_good():
    ok, reason = local_test_auth('8186A1')#jonah's fob. Should be good
    assert ok
    assert reason == 'access is always granted'



def local_test_auth(tag):
    controller.log_file = "rpi/test_files/test_logs.txt"
    members = Members(filename="rpi/test_files/testMembers.csv")
    roles = Roles(filename="rpi/test_files/testRoles.csv")
    ok, reason = test_auth(tag, members, roles)
    return ok, reason