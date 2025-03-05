import os
from pathlib import Path
from src.testsolar_python_unittest.collector import (
    _get_target_case_module,
    _get_available_module_name,
)


def test_get_target_case_module():
    os.environ["TESTSOLAR_TTP_TARGETCASEMODULE"] = "testcases"
    modules = _get_target_case_module()
    assert modules == ["testcases"]

    os.environ["TESTSOLAR_TTP_TARGETCASEMODULE"] = "testcases,  testcases02"
    modules = _get_target_case_module()
    assert modules == ["testcases", "testcases02"]

    os.environ["TESTSOLAR_TTP_TARGETCASEMODULE"] = ""
    modules = _get_target_case_module()
    assert not modules


def test_get_available_module_name():
    testdata_dir: str = str(Path(__file__).parent.absolute().joinpath("testdata"))
    assert _get_available_module_name(testdata_dir, "test_demo01") == "test_demo01"
    assert _get_available_module_name(testdata_dir, "test_demo02") == "test_demo02.py"
    assert (
        _get_available_module_name(testdata_dir, "test_demo02.py") == "test_demo02.py"
    )
