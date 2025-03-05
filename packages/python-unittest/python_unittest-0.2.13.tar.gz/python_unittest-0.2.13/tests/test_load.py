import json
import os
from pathlib import Path

from src.load import collect_testcases_from_args
from testsolar_testtool_sdk.file_reader import read_file_load_result

testdata_dir: str = str(Path(__file__).parent.absolute().joinpath("testdata"))


def test_collect_all_testcases():
    with open(os.path.join(testdata_dir, "test_entry.json"), "w") as f:
        content = {
            "TaskId": "aa",
            "ProjectPath": testdata_dir,
            "FileReportPath": os.path.join(testdata_dir, "results.json"),
            "Collectors": [],
            "Context": {},
            "TestSelectors": ["."],
        }
        json.dump(content, f)
    collect_testcases_from_args(
        args=["load.py", Path.joinpath(Path(testdata_dir), "test_entry.json")],
        workspace=testdata_dir,
    )
    re = read_file_load_result(
        file_report_path=Path(os.path.join(testdata_dir, "results.json"))
    )
    assert len(re.Tests) == 6
    assert len(re.LoadErrors) == 1


def test_collect_file():
    with open(os.path.join(testdata_dir, "test_entry.json"), "w") as f:
        content = {
            "TaskId": "aa",
            "ProjectPath": testdata_dir,
            "FileReportPath": os.path.join(testdata_dir, "results.json"),
            "Collectors": [],
            "Context": {},
            "TestSelectors": ["test_demo02.py"],
        }
        json.dump(content, f)
    collect_testcases_from_args(
        args=["load.py", Path.joinpath(Path(testdata_dir), "test_entry.json")],
        workspace=testdata_dir,
    )
    re = read_file_load_result(
        file_report_path=Path(os.path.join(testdata_dir, "results.json"))
    )
    assert len(re.Tests) == 2
    assert not re.LoadErrors


def test_collect_dir():
    with open(os.path.join(testdata_dir, "test_entry.json"), "w") as f:
        content = {
            "TaskId": "aa",
            "ProjectPath": testdata_dir,
            "FileReportPath": os.path.join(testdata_dir, "results.json"),
            "Collectors": [],
            "Context": {},
            "TestSelectors": ["test_demo01"],
        }
        json.dump(content, f)
    collect_testcases_from_args(
        args=["load.py", Path.joinpath(Path(testdata_dir), "test_entry.json")],
        workspace=testdata_dir,
    )
    re = read_file_load_result(
        file_report_path=Path(os.path.join(testdata_dir, "results.json"))
    )
    assert len(re.Tests) == 4
    assert len(re.LoadErrors) == 1
