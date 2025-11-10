import os
from typing import List


def read_file(file_name) -> List[str]:
    """
    读取文本文件，返回list[str]
    """
    lines: List[str] = []
    if not os.path.exists(file_name):
        return lines

    # Read file and skip header/meta lines until actual data lines are found.
    # Data lines typically start with a digit (year) like '2022-01-01...' or '2022/01/01,...'.
    with open(file_name, 'r', encoding='utf-8', errors='ignore') as f:
        for raw in f:
            line = raw.strip()
            if not line:
                continue
            # If the first non-space char is a digit, we treat it as a data line.
            # This skips header lines like 'dt,open,high,...' or descriptive text.
            if line[0].isdigit():
                lines.append(line)
            else:
                # skip non-data/header lines
                continue

    return lines


def write_file(file_name, lines: List[str], append: bool):
    """
    写文件， append为True表示追加，否则重新创新
    """
    if append:
        with open(file_name, 'a') as f:
            for line in lines:
                f.write(F"{line}\n")
            f.flush()
    else:
        with open(file_name, 'w') as f:
            for line in lines:
                f.write(F"{line}\n")
            f.flush()
