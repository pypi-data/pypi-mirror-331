import os
from typing import Iterator, List, Set, Tuple

from loguru import logger
from testsolar_testtool_sdk.model.load import LoadResult, LoadError
from testsolar_testtool_sdk.model.param import EntryParam
from testsolar_testtool_sdk.model.test import TestCase
from testsolar_testtool_sdk.reporter import FileReporter
import unittest
import urllib.parse
import inspect
from pathlib import Path


def list_testsuite(test_suite: unittest.TestSuite) -> Iterator[unittest.TestCase]:
    """获取testsuite中的TestCase实例列表"""
    for item in test_suite:
        if isinstance(item, unittest.TestSuite):
            for it in list_testsuite(item):
                yield it
        else:
            yield item


def get_load_results_from_test_suite(
    proj_root: str, test_suite: unittest.TestSuite
) -> Tuple[list[TestCase], list[LoadError]]:
    testcase_list: list[TestCase] = []
    load_error_list: list[LoadError] = []
    for it in list_testsuite(test_suite):
        if it.__class__.__name__ == "ModuleImportFailure":
            try:
                it.debug()
            except Exception as e:
                err_msg = e.message.strip()  # type: ignore
                logger.error(
                    f"load testcase {it._testMethodName} failed, err: {err_msg}"
                )
                load_error_list.append(
                    LoadError(name=it._testMethodName, message=err_msg)
                )
        elif it.__class__.__name__ == "_FailedTest":
            err_msg = it._exception.msg  # type: ignore
            logger.error(f"load testcase {it._testMethodName} failed, err: {err_msg}")
            load_error_list.append(LoadError(name=it._testMethodName, message=err_msg))
        else:
            class_file_path = inspect.getfile(it.__class__)
            rel_path = os.path.relpath(class_file_path, proj_root)
            name = f"{rel_path}?{it.__class__.__name__}/{it._testMethodName}"
            logger.info(f"load testcase: {name}")
            testcase_list.append(
                TestCase(
                    Name=name,
                    Attributes={
                        "description": (
                            getattr(it, it._testMethodName).__doc__ or ""
                        ).strip(),
                    },
                )
            )
    return testcase_list, load_error_list


def parse_testcases(
    proj_root: str, test_selectors: list[str]
) -> Tuple[list[TestCase], list[LoadError]]:
    """解析测试用例"""
    testcase_list: list[TestCase] = []
    load_error_list: list[LoadError] = []
    for selector in test_selectors:
        test_loader = unittest.TestLoader()
        abs_path = os.path.join(proj_root, selector)
        if os.path.isfile(abs_path):
            dir_name = os.path.dirname(abs_path)
            file_name = os.path.basename(abs_path)
            test_suite = test_loader.discover(start_dir=dir_name, pattern=file_name)
        elif os.path.isdir(abs_path):
            test_suite = test_loader.discover(start_dir=abs_path)
        else:
            logger.error(f"can't find path {abs_path}")
            continue
        testcases, load_errors = get_load_results_from_test_suite(proj_root, test_suite)
        testcase_list.extend(testcases)
        load_error_list.extend(load_errors)
    logger.info(
        f"get {len(testcase_list)} testcases and {len(load_error_list)} load errors"
    )
    return testcase_list, load_error_list


def _should_collect_all_testcases(selectors: List[str]) -> bool:
    return len(selectors) == 1 and (selectors[0] == "." or selectors[0] == "/")


def _get_target_case_module() -> List[str]:
    case_dir = os.getenv("TESTSOLAR_TTP_TARGETCASEMODULE", "")
    if case_dir and case_dir.strip():
        logger.info("case target directories: {}".format(case_dir))
        return [d.strip() for d in case_dir.split(",")]
    return []


def _get_available_module_name(proj_path: str, module: str) -> str:
    abs_path = os.path.join(proj_path, module)
    if os.path.isdir(abs_path):
        return module
    elif os.path.isfile(abs_path):
        return module
    elif os.path.isfile(f"{abs_path}.py"):
        return f"{module}.py"
    else:
        logger.error(f"unavailable target module: {module}")
        return ""


def collect_testcases(entry_param: EntryParam) -> None:
    logger.info(
        f"loading testcase from workdir [{entry_param.ProjectPath}], selectors: {entry_param.TestSelectors}, task id: {entry_param.TaskId}"
    )
    deduplicated_selectors: Set[str] = set()
    if not entry_param.TestSelectors:
        logger.info("lack of test selectors, use default value: .")
        entry_param.TestSelectors = ["."]
    if _should_collect_all_testcases(selectors=entry_param.TestSelectors):
        if target_case_modules := _get_target_case_module():
            modules = [
                _get_available_module_name(
                    proj_path=entry_param.ProjectPath, module=module
                )
                for module in target_case_modules
            ]
            deduplicated_selectors = {module for module in modules if module}
        else:
            for item in os.listdir(entry_param.ProjectPath):
                if item.startswith(".") or item.startswith("_"):
                    continue
                abs_path = os.path.join(entry_param.ProjectPath, item)
                if os.path.isdir(abs_path):
                    deduplicated_selectors.add(item)
                elif os.path.isfile(abs_path) and abs_path.endswith(".py"):
                    deduplicated_selectors.add(item)
    else:
        for selector in entry_param.TestSelectors:
            url = urllib.parse.urlparse(selector)
            deduplicated_selectors.add(url.path)
    logger.info(f"try to load testcases from {deduplicated_selectors}")
    tests, load_errors = parse_testcases(
        proj_root=entry_param.ProjectPath, test_selectors=list(deduplicated_selectors)
    )
    load_result: LoadResult = LoadResult(
        Tests=tests,
        LoadErrors=load_errors,
    )
    reporter = FileReporter(report_path=Path(entry_param.FileReportPath))
    reporter.report_load_result(load_result)
