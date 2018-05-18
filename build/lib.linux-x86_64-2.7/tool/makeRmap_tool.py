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

import sys
from rtree import index
import os


from utils import logger

try:
    if hasattr(sys, '_run_from_cmdl') is True:
        raise ImportError
    from pycompss.api.parameter import FILE_IN, FILE_OUT, IN
    from pycompss.api.task import task
    from pycompss.api.api import compss_wait_on
except ImportError:
    logger.warn("[Warning] Cannot import \"pycompss\" API packages.")
    logger.warn("          Using mock decorators.")

    from utils.dummy_pycompss import FILE_IN, FILE_OUT, IN  # pylint: disable=ungrouped-imports
    from utils.dummy_pycompss import task # pylint: disable=ungrouped-imports
    from utils.dummy_pycompss import compss_wait_on # pylint: disable=ungrouped-imports


from basic_modules.tool import Tool
from basic_modules.metadata import Metadata

import re
re.compile("pattern")

####################################################

class makeRmapFile(Tool):

    """
    Tool for digest the genome with one RE. Wrapper of hicup_digester
    """


    def __init__(self, configuration=None):
        """
        initialising the function

        Parameters:
        -----------
        configuration: dict
            dictionary containing all the arguments and parameters
            to run the tool
        """

        print("makeRmapFile initialising")
        Tool.__init__(self)

        if configuration is None:
            configuration = {}

        self.configuration.update(configuration)



    def iupac2regex(self, restring):
        """
        Convert target sites with IUPAC nomenclature to regex pattern
        """
        restring = restring.replace('R', '[AG]')
        restring = restring.replace('Y', '[CT]')
        restring = restring.replace('M', '[AC]')
        restring = restring.replace('K', '[GT]')
        restring = restring.replace('S', '[CG]')
        restring = restring.replace('W', '[AT]')
        restring = restring.replace('H', '[ACT]')
        restring = restring.replace('B', '[CGT]')
        restring = restring.replace('V', '[ACG]')
        restring = restring.replace('D', '[AGT]')
        restring = restring.replace('N', '[ATGC]')
        return restring

    def genome_to_dict(self, genome_fa):
        """
        This function takes a genome file in fasta format
        and converts it into a dictionary

        Parameters:
        ----------
        genome_fa : str
            entire path to the genome in fasta file

        Returns:
        --------
            dict
            genome in a dict form, key as chromosomes and
            values str with sequences
        """
        logger.info("converting fasta genome into a dictionary")
        genome_dict = {}
        sequence = ""

        with open(genome_fa, "r") as file_handle:
            for line in file_handle:
                line = line.rstrip()
                if line[0] == ">":
                    if not sequence:
                        genome_dict[int(line[4:])] = []
                        chromo = int(line[4:])
                        continue
                    else:
                        genome_dict[chromo] = sequence
                        chromo = int(line[4:])
                        sequence = ""
                        continue

                sequence += line
            #Ad last chromosome
            genome_dict[chromo] = sequence

        return genome_dict

    def map_re_sites2(
            self, enzyme_name, genome_seq, out_dir_makeRmap, out_prefix_makeRmap,
            Rtree_files, verbose=False):
        """
        map all restriction enzyme (RE) sites of a given enzyme in a genome.
        Position of a RE site is defined as the genomic coordinate of the first
        nucleotide before the first cut (genomic coordinate starts at 1).
        In the case of HindIII the genomic coordinate is this one:
        123456 789...
             |
             v
        -----A|AGCT T--------------
        -----T TCGA|A--------------
        In this example the coordinate of the RE site would be 6.


        Parameters:
        -----------
        enzyme_name: dict
            name of the enzyme to map (upper/lower case are
            important) as key and value the target sequence
            with a pipe where the enzyme cuts

        genome_seq: str
            genome in fasta format


        Return
        ------
            bool
            Fragments
        """
        enzymes = enzyme_name

        #the genome should be in a dictionary
        genome_seq = self.genome_to_dict(genome_seq)

        # we match the full cut-site but report the position after the cut site
        # (third group of the regexp)
        restring = ('%s') % (
            '|'.join(
                [
                    '(?<=%s(?=%s))' % tuple(enzymes[n].split('|'))
                    for n in enzymes]
                )
            )

        # IUPAC conventions
        restring = self.iupac2regex(restring)

        enz_pattern = re.compile(restring)

        frags = {}
        count = 0

        logger.info("searching RE sites")

        for crm in genome_seq:
            seq = genome_seq[crm]
            frags[crm] = []
            for match in enz_pattern.finditer(seq):
                pos = match.end()
                frags[crm].append(pos)
                count += 1
            # at the end of last chunk we add the chromosome length
            frags[crm].append(len(seq))
        if verbose:
            print ('Found %d RE sites' % count)

        print(frags)

        self.from_frag_to_rmap(frags, out_dir_makeRmap, out_prefix_makeRmap, Rtree_files)

    def from_frag_to_rmap(self, frags, out_dir_makeRmap, out_prefix_makeRmap, Rtree_files):
        """
        This function takes the fragment output from digestion and
        convert them into rmap files.

        It also save the RE sites positions and ID into a file using Rtree
        python module. This file will be used by makeBatmap.py to generate
        .batmap file using spatial indexing

        Parameters:
        -----------
        frags : dict
            dict containing chromosomes as keys and
            RE sites as values
        out_dir_makeRmap: str
            path to the output directory
        out_prefix_makeRmap: str
            name of the output file.
        """

        logger.info("coverting RE fragments into rmap file")

        idx = index.Rtree(Rtree_files)

        with open(out_dir_makeRmap + out_prefix_makeRmap + ".rmap", "w") as out:
            counter_id = 0
            for crm in frags:
                counter = 0
                for RE_site in frags[crm]:
                    counter_id += 1
                    counter += 1
                    if counter == 1:
                        print("{}\t{}\t{}\t{}".format(str(crm), 1,
                                                      RE_site, counter_id),
                              file=out)
                        idx.insert(counter_id, (1, crm, RE_site, crm))
                    else:
                        print("{}\t{}\t{}\t{}".format(str(crm),
                                                      prev_RE_site+1, RE_site, counter_id),
                              file=out)
                        idx.insert(counter_id, (prev_RE_site+1, crm, RE_site, crm))

                    prev_RE_site = RE_site

        idx.close()

        if os.path.getsize(out_dir_makeRmap + out_prefix_makeRmap + ".rmap") > 0:
            return True

        logger.fatal("makeRmap_Tool.py failed to generate .rmap file")
        return False

    def run(self, input_files, input_metadata, output_files):
        """
        This function run the tool

        Parameters
        ----------

        input_files: dict
            genome in fasta file
        input_metadata: dict
            input metadata

        Returns
        -------

        output_files: dict
            name and path to the output file
        output_metadata: dict
            lest of matching metadata
        """

        results = self.map_re_sites2(
            self.configuration["RE"],
            input_files["genome"],
            output_files["out_dir_makeRmap"],
            output_files["out_prefix_makeRmap"],
            output_files["Rtree_files"]
            )

        results = compss_wait_on(results)

        output_metadata = {
            "rmap": Metadata(
                data_type=input_metadata['genome_digest'].data_type,
                file_type="rmap",
                file_path=output_files["out_dir_makeRmap"],
                sources=[
                    input_metadata["genome_digest"].file_path,
                ],
                taxon_id=input_metadata["genome_digest"].taxon_id,
                meta_data={
                    "RE" : input_metadata["genome_digest"].meta_data,
                    "tool": "makeRmapFileTool"
                }
            )
        }

        return(results, output_metadata)


if __name__ == "__main__":

    path = "../tests/data/"


    configuration = {"RE" : {"HindIII" : 'A|AGCTT'}
                    }

    input_files = {
        "genome" : path + "test_makeRmap/toy_hg19.fa",
        }


    metadata = {"genome_digest" : Metadata(
        "hg38", "fasta", path+ "test_makeRmap/toy_hg19.fa",
        None, "HindIII", 9606),
        }


    output_files = {
        "out_dir_makeRmap" : path + "/test_makeRmap/",
        "out_prefix_makeRmap" : "restriction_enzyme_test_HindIII_hg19",
        "Rtree_files" : path + "/test_makeRmap/rtree_file"
        }

    makeRmap_handle = makeRmapFile(configuration)
    print(makeRmap_handle.run(input_files, metadata, output_files))