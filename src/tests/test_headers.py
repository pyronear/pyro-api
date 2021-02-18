# Copyright (C) 2021, Pyronear contributors.

# This program is licensed under the Apache License version 2.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0.txt> for full license details.

from pathlib import Path

@pytest.fixture(scope="module")
def header_options():
    shebang = ["#!usr/bin/python\n"]
    blank_line = "\n"

    copyright_notice = ["# Copyright (C) 2021, Pyronear contributors.\n"]
    license_notice = [
        "# This program is licensed under the Apache License version 2.\n",
        "# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0.txt> for full license details.\n"
    ]

    return [
        shebang + [blank_line] + copyright_notice + [blank_line] + license_notice,
        copyright_notice + [blank_line] + license_notice
    ]

@pytest.fixture(scope="module")
def excluded_files():
    return ["version.py", "__init__.py"]


def test_headers(header_options, excluded_files):
    # For every python file in the repository
    for source_path in Path(__file__).parent.parent.parent.rglob('*.py'):
        if source_path.name not in excluded_files:
            # Parse header
            header_length = max(len(option) for option in header_options)
            current_header = []
            with open(source_path) as f:
                for idx, line in enumerate(f):
                    current_header.append(line)
                    if idx == header_length - 1:
                        break

            # Compare it
            self.assertTrue(any("".join(current_header[:min(len(option), len(current_header))]) == "".join(option)
                                for option in header_options), msg=f"Invalid header in {source_path}")
