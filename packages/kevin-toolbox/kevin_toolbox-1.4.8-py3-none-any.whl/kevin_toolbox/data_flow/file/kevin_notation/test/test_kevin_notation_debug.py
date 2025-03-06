import pytest
from kevin_toolbox.patches.for_test import check_consistency

import os
import numpy as np

from kevin_toolbox.data_flow.file import kevin_notation
from kevin_toolbox.data_flow.file.kevin_notation.test.test_data.data_all import metadata_ls, content_ls, file_path_ls


@pytest.mark.parametrize("expected_metadata, expected_content, file_path",
                         zip(metadata_ls, content_ls, file_path_ls))
def test_write(expected_metadata, expected_content, file_path):
    print("test write()")

    """
    当写入的列的元素不一致时，是否能正常报错
    """

    # 新建
    file_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "test_data/temp", os.path.basename(file_path))

    # 字典方式写入
    if len(expected_content) > 1:
        with pytest.raises(AssertionError):
            list(expected_content.values())[0].clear()
            kevin_notation.write(metadata=expected_metadata, content=expected_content, file_path=file_path)
