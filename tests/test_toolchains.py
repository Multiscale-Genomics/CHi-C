"""
.. See the NOTICE file distributed with this work for additional information
   regarding copyright ownership.

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

from __future__ import print_function

import argparse
import subprocess
import pytest  # pylint: disable=unused-import


def all_toolchain(verbose=False):
    """
    Runs the tests for all of the tools

    This set is only required for determining code coverage.
    """

    params = []

    if verbose is True:
        params.append('-')

    #params.append('test_gem_indexer.py')
    params.append('test_truncater.py')
    params.append('test_makeRmap_Tool.py')
    params.append('test_makeBaitmap.py')
    params.append('test_makeDesignFiles_Tool.py')
    params.append('test_fastq2bed.py')
    params.append('test_bed2bamchicago.py')
    params.append('test_bam2chicago_Tool.py')
    #params.append('test_runChicago.py')

    return pytest.main(params)

if __name__ == "__main__":
    import sys
    sys._run_from_cmdl = True # pylint: disable=protected-access

    PARSER = argparse.ArgumentParser(description="Test for running all tools in a chain")
    PARSER.add_argument("--verbose", action="store_const", const=True, default=False)

    ARGS = PARSER.parse_args()

    VERBOSE = ARGS.verbose

    all_toolchain()