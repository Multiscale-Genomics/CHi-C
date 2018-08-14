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

import os
from basic_modules.metadata import Metadata

from process_truncater import process_truncater

def test_truncater():
    """
    Test for the truncater function
    """

    path = os.path.join(os.getcwd(), "data/test_truncater/")

    input_files = {
        "fastq1" : path + "SRR3535023_1.fastq",
        "fastq2" : path + "SRR3535023_2.fastq"
    }

    metadata = {
        "fastq1": Metadata(
            data_type="text",
            file_type="fastq",
            file_path=input_files["fastq1"],
            sources="",
            taxon_id=9606,
            meta_data=""
        ),
        "fastq2": Metadata(
            data_type="text",
            file_type="fastq",
            file_path=input_files["fastq2"],
            sources="",
            taxon_id=9606,
            meta_data=""
        )
    }

    output_files = {
        "fastq1_trunc" : path + "SRR3535023_1.trunc.fastq",
        "fastq2_trunc" : path + "SRR3535023_2.trunc.fastq",
        "hicup_summary" : path + "hicup_truncater_summary_.txt",
        "barchat_fastq1" : path + "SRR3535023_1.fastq.truncation_barchart.svg",
        "barchat_fastq2" : path + "SRR3535023_2.fastq.truncation_barchart.svg"
    }

    configuration = {
        "quiet_progress": True,
        "RE_truncater": "A^AGCT",
        "threads" : "2",
        "outdir" : path
    }

    truncater_hdl = process_truncater(configuration)
    truncater_hdl.run(input_files, metadata, output_files)

    assert os.path.isfile(output_files["fastq1_trunc"]) is True
    assert os.path.isfile(output_files["fastq1_trunc"]) is True

    assert os.path.getsize(output_files["fastq1_trunc"]) > 0
    assert os.path.getsize(output_files["fastq1_trunc"]) > 0