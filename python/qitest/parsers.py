## Copyright (c) 2012-2014 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Collection of parser fonctions for qitests actions
"""

import copy
import os

from qisys import ui
import qisys.parsers
import qibuild.parsers
import qitest.project

def test_parser(parser, with_num_jobs=True):
    qisys.parsers.worktree_parser(parser)
    group = parser.add_argument_group("test options")
    group.add_argument("--perf", dest="perf", action="store_true",
                        help="run perfs tests instead of pure tests.")
    group.add_argument("-k", "--pattern", dest="pattern",
                        help="Filter tests matching this pattern")
    group.add_argument("-V", dest="verbose_tests", action="store_true",
                        help="display tests output")
    group.add_argument("--valgrind", dest="valgrind", action="store_true",
                        help="run tests under valgrind")
    group.add_argument("--nightmare", dest="nightmare", action="store_true",
                        help="run tests in shuffle and 20 times (apply only to gtest)")
    group.add_argument("--coverage", dest="coverage", action="store_true",
                        help="run coverage")
    group.add_argument("--ncpu", dest="num_cpus", default=-1, type=int,
                        help="set number of CPU each test is allowed to use (linux)")
    group.add_argument("--nightly", action="store_true", dest="nightly")
    group.add_argument("--qitest-json", dest="qitest_jsons", action="append")
    parser.set_defaults(nightly=False)
    if with_num_jobs:
        group.add_argument("-j", dest="num_jobs", default=1, type=int,
                            help="Number of tests to run in parallel")
    return group

def get_test_runner(args, project_name=None, qitest_json=None):
    project_names = args.projects or list()
    if project_name:
        project_names = [project_name]
    else:
        project_names = args.projects

    test_project = None
    if not qitest_json:
        qitest_json = vars(args).get("qitest_json")
    if not qitest_json:
        candidate = os.path.join(os.getcwd(), "qitest.json")
        if os.path.exists(candidate):
            qitest_json = candidate
    if qitest_json:
        test_project = qitest.project.TestProject(qitest_json)
    if not test_project:
        try:
            build_worktree = qibuild.parsers.get_build_worktree(args)

            new_args = copy.deepcopy(args)
            new_args.projects = project_names
            build_project = qibuild.parsers.get_one_build_project(build_worktree, new_args)
            test_project = build_project.to_test_project()
            build_project = True
        except:
            ui.error("Error when parsing arguments")
            raise

    if args.coverage and not build_project:
        raise Exception("""\
--coverage can only be used from a qibuild CMake project
""")


    test_runner = qibuild.test_runner.ProjectTestRunner(test_project)

    test_runner.pattern = args.pattern
    test_runner.perf = args.perf
    test_runner.coverage = args.coverage
    test_runner.valgrind = args.valgrind
    test_runner.verbose = args.verbose_tests
    test_runner.num_cpus = args.num_cpus
    test_runner.num_jobs = args.num_jobs
    test_runner.nightly = args.nightly

    return test_runner

def get_test_runners(args):
    res = list()
    qitest_jsons = args.qitest_jsons or list()
    project_names = args.projects or list()
    if not qitest_jsons and not project_names:
        return [get_test_runner(args)]

    for qitest_json in qitest_jsons:
        res.append(get_test_runner(args, qitest_json=qitest_json))
    for project_name in project_names:
        res.append(get_test_runner(args, project_name=project_name))

    return res
