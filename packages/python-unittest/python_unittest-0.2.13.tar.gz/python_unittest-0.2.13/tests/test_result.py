import os
from pathlib import Path
from src.testsolar_python_unittest.executor import parse_test_report

testdata_dir: str = str(Path(__file__).parent.absolute().joinpath("testdata"))


def test_parse_test_report():
    parse_test_report(os.path.join(testdata_dir, "xml_results.xml"))
