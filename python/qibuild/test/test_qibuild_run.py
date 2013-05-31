import pytest
import os

from qibuild.test.conftest import QiBuildAction
from qitoolchain.test.conftest import QiToolchainAction
from qibuild.actions import run

def test_run_target(qibuild_action):
    qibuild_action.add_test_project("testme")
    qibuild_action("configure", "testme")
    qibuild_action("make", "testme")

    retcode = qibuild_action("run", "ok", retcode=True)
    assert retcode == 0

def test_run_failing_binary(qibuild_action):
    qibuild_action.add_test_project("testme")
    qibuild_action("configure", "testme")
    qibuild_action("make", "testme")


    retcode = qibuild_action("run", "fail", retcode=True)
    assert retcode == 1

def test_run_segfaulting_binary(qibuild_action, record_messages):
    qibuild_action.add_test_project("testme")
    qibuild_action("configure", "testme")
    qibuild_action("make", "testme")

    retcode = qibuild_action("run", "segfault", retcode=True)
    if os.name != 'nt':
        # on Windows the python process may be interrupted by
        # the OS with a pop up 'segfault_d.exe has stopped working'
        # so we may not get the error message
        assert record_messages.find("Process crashed")
    assert retcode != 0

def test_run_failure(qibuild_action):
    qibuild_action.add_test_project("testme")
    qibuild_action("configure", "testme")
    qibuild_action("make", "testme")

    e = qibuild_action("run", "idontexist", raises=True)
    assert e == "idontexist not found"
