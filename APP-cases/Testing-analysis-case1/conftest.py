# coding=utf-8

import pytest
from common.base_method import BasePageMethod


@pytest.fixture(scope="session")
def func():
    lib = BasePageMethod()
    yield lib
    lib.driver.close()
    lib.driver.quit()
