import os
import pytest
import pandas as pd
from VCFtoProteogenomics import get_cds_pos
from VCFtoProteogenomics import introduce_mut2cds
from VCFtoProteogenomics import get_aminoacid_ref_pos_alt
from VCFtoProteogenomics import prepare_vcf
from Bio import SeqIO
import pybedtools
import tempfile
import filecmp


def setup_get_cds_pos_case1():
    """
        case 1 = non-syn variation, + strand
        please refer to https://www.ensembl.org/Homo_sapiens/Variation/Explore?db=core;g=ENSG00000141568;r=17:82571798-82571864;source=dbSNP;t=ENST00000473637;v=rs747228346;vdb=variation;vf=365767866
    """
    exons = {}
    exons[1] = [82519889, 82520307, 0]
    exons[2] = [82563354, 82563548, 1]
    exons[3] = [82568054, 82568201, 1]
    exons[4] = [82571724, 82571870, 0]
    exons[5] = [82582741, 82582934, 0]
    exons[6] = [82584013, 82584188, 1]
    exons[7] = [82585904, 82586200, 2]
    exons[8] = [82587063, 82587272, 2]
    exons[9] = [82595782, 82595837, 2]
    exon_number = 4
    df = pd.DataFrame({
        'chr': [17],
        'ref': ['C'],
        'alt': ['T'],
        'pos': [82571818],
        'strand': ['+']
    })
    row = df.iloc[0]
    return (exons, exon_number, row)


def setup_introduce_mut2cds_case1():
    test_file = "./VCFtoProteogenomics_test_files/cds_ENST00000473637.fasta"
    cds_file = SeqIO.index(test_file, 'fasta')
    return (cds_file['ENST00000473637'], cds_file['ENST00000473637_c.857:C>T'])


def test_get_cds_pos_case1():
    expected_cds_pos = 857 - 1
    # expected_ref_aa = 'T'
    # expected_alt_aa = 'I'
    exons, exon_number, row = setup_get_cds_pos_case1()
    cds_pos = get_cds_pos(exons, exon_number, row)
    message = "The expected cds_pos {}".format(expected_cds_pos)
    message = message + "doesn't match the calculated on {}".format(cds_pos)
    assert expected_cds_pos == cds_pos, message


def test_introduce_mut2cds_case1():
    _, _, row = setup_get_cds_pos_case1()
    seq, expected_seq_mut = setup_introduce_mut2cds_case1()
    cds_pos = 857 - 1
    seq_mut = introduce_mut2cds(row, cds_pos, str(seq.seq))
    assert str(
        expected_seq_mut.seq) == seq_mut, "introduce_mut2seq() went wrong"


def test_get_aminoacid_ref_pos_alt_case1():
    _, _, row = setup_get_cds_pos_case1()
    seq, seq_mut = setup_introduce_mut2cds_case1()
    cds_pos = 857 - 1
    expected_aa_ref = "T"
    expected_aa_alt = "I"
    expected_aa_pos = 286
    aa_ref, aa_pos, aa_alt = get_aminoacid_ref_pos_alt(row,
                                                       str(seq.seq),
                                                       str(seq_mut.seq),
                                                       cds_pos,
                                                       to_stop=True)
    assert expected_aa_ref == aa_ref, "get_aminoacid_ref_pos_alt() went wrong"
    assert expected_aa_pos == aa_pos, "get_aminoacid_ref_pos_alt() went wrong"
    assert expected_aa_alt == aa_alt, "get_aminoacid_ref_pos_alt() went wrong"


# case 2 : insertion, strand +
def setup_get_cds_pos_case2():
    """
        case 2 = inframe insertion, + strand
        please refer to https://www.ensembl.org/Homo_sapiens/Variation/Explore?db=core;g=ENSG00000141568;r=17:82519713-82602392;t=ENST00000473637;v=rs1461045605;vdb=variation;vf=380268121
    """
    exons = {}
    exons[1] = [82519889, 82520307, 0]
    exons[2] = [82563354, 82563548, 1]
    exons[3] = [82568054, 82568201, 1]
    exons[4] = [82571724, 82571870, 0]
    exons[5] = [82582741, 82582934, 0]
    exons[6] = [82584013, 82584188, 1]
    exons[7] = [82585904, 82586200, 2]
    exons[8] = [82587063, 82587272, 2]
    exons[9] = [82595782, 82595837, 2]
    exon_number = 1
    df = pd.DataFrame({
        'chr': [17],
        'ref': ['C'],
        'alt': ['CGGGCGGCGGGGCCGG'],
        'pos': [82519935],
        'strand': ['+']
    })
    row = df.iloc[0]
    return (exons, exon_number, row)


def setup_introduce_mut2cds_case2():
    test_file = "./VCFtoProteogenomics_test_files/cds_ENST00000473637.fasta"
    cds_file = SeqIO.index(test_file, 'fasta')
    return (cds_file['ENST00000473637'],
            cds_file['ENST00000473637_c.47:C>CGGGCGGCGGGGCCGG'])


def test_get_cds_pos_case2():
    expected_cds_pos = 47 - 1
    exons, exon_number, row = setup_get_cds_pos_case2()
    cds_pos = get_cds_pos(exons, exon_number, row)
    message = "The expected cds_pos {}".format(expected_cds_pos)
    message = message + "doesn't match the calculated on {}".format(cds_pos)
    assert expected_cds_pos == cds_pos, message


def test_introduce_mut2cds_case2():
    _, _, row = setup_get_cds_pos_case2()
    seq, expected_seq_mut = setup_introduce_mut2cds_case2()
    cds_pos = 47 - 1
    seq_mut = introduce_mut2cds(row, cds_pos, str(seq.seq))
    assert str(
        expected_seq_mut.seq) == seq_mut, "introduce_mut2seq() went wrong"


# case 3 : deletion, strand +
def setup_get_cds_pos_case3():
    """
        case 3 = inframe deletion, + strand
        please refer to https://www.ensembl.org/Homo_sapiens/Variation/Explore?db=core;g=ENSG00000141568;r=17:82519713-82602392;t=ENST00000473637;v=rs779355780;vdb=variation;vf=366765189
    """
    exons = {}
    exons[1] = [82519889, 82520307, 0]
    exons[2] = [82563354, 82563548, 1]
    exons[3] = [82568054, 82568201, 1]
    exons[4] = [82571724, 82571870, 0]
    exons[5] = [82582741, 82582934, 0]
    exons[6] = [82584013, 82584188, 1]
    exons[7] = [82585904, 82586200, 2]
    exons[8] = [82587063, 82587272, 2]
    exons[9] = [82595782, 82595837, 2]
    exon_number = 1
    df = pd.DataFrame({
        'chr': [17],
        'ref': ['CGGGCGGCGGGGCCGG'],
        'alt': ['C'],
        'pos': [82519935],
        'strand': ['+']
    })
    row = df.iloc[0]
    return (exons, exon_number, row)


def setup_introduce_mut2cds_case3():
    test_file = "./VCFtoProteogenomics_test_files/cds_ENST00000473637.fasta"
    cds_file = SeqIO.index(test_file, 'fasta')
    return (cds_file['ENST00000473637'], cds_file['ENST00000473637_c.47:del'])


def test_get_cds_pos_case3():
    expected_cds_pos = 47 - 1
    exons, exon_number, row = setup_get_cds_pos_case3()
    cds_pos = get_cds_pos(exons, exon_number, row)
    message = "The expected cds_pos {}".format(expected_cds_pos)
    message = message + "doesn't match the calculated on {}".format(cds_pos)
    assert expected_cds_pos == cds_pos, message


def test_introduce_mut2cds_case3():
    _, _, row = setup_get_cds_pos_case3()
    seq, expected_seq_mut = setup_introduce_mut2cds_case3()
    cds_pos = 47 - 1
    seq_mut = introduce_mut2cds(row, cds_pos, str(seq.seq))
    assert str(
        expected_seq_mut.seq) == seq_mut, "introduce_mut2seq() went wrong"


# case 4 : non syn variant, negative strand
def setup_get_cds_pos_case4():
    """
        case 4 = non syn, - strand
        please refer to https://www.ensembl.org/Homo_sapiens/Variation/Explore?db=core;g=ENSG00000055483;r=17:78802461-78840864;t=ENST00000588086;v=rs773813684;vdb=variation;vf=366593845
    """
    exons = {}
    exons[3] = [78836111, 78836363, 0]
    exons[4] = [78835280, 78835501, 2]
    exons[5] = [78828897, 78829007, 2]
    exons[6] = [78827245, 78827347, 2]
    exons[7] = [78821937, 78822004, 1]
    exons[8] = [78820991, 78821061, 2]
    exons[9] = [78819930, 78820012, 0]
    exons[10] = [78818667, 78818778, 1]
    exons[11] = [78814412, 78814552, 0]
    exons[12] = [78813773, 78813873, 0]
    exons[13] = [78812860, 78813001, 1]
    exons[14] = [78806959, 78807636, 0]
    exons[15] = [78806156, 78806286, 0]
    exons[16] = [78803385, 78803978, 1]
    exons[17] = [78802461, 78802535, 1]
    exon_number = 3
    df = pd.DataFrame({
        'chr': [17],
        'ref': ['C'],
        'alt': ['G'],
        'pos': [78836336],
        'strand': ['-']
    })
    row = df.iloc[0]
    return (exons, exon_number, row)


def setup_introduce_mut2cds_case4():
    test_file = "./VCFtoProteogenomics_test_files/cds_ENST00000588086.fasta"
    cds_file = SeqIO.index(test_file, 'fasta')
    return (cds_file['ENST00000588086'], cds_file['ENST00000588086_c.28:G>C'])


def test_get_cds_pos_case4():
    expected_cds_pos = 28 - 1
    exons, exon_number, row = setup_get_cds_pos_case4()
    cds_pos = get_cds_pos(exons, exon_number, row)
    message = "The expected cds_pos {}".format(expected_cds_pos)
    message = message + "doesn't match the calculated on {}".format(cds_pos)
    assert expected_cds_pos == cds_pos, message


def test_get_aminoacid_ref_pos_alt_case4():
    _, _, row = setup_get_cds_pos_case4()
    seq, seq_mut = setup_introduce_mut2cds_case4()
    cds_pos = 28 - 1
    expected_aa_ref = "A"
    expected_aa_alt = "P"
    expected_aa_pos = 10
    aa_ref, aa_pos, aa_alt = get_aminoacid_ref_pos_alt(row,
                                                       str(seq.seq),
                                                       str(seq_mut.seq),
                                                       cds_pos,
                                                       to_stop=True)
    assert expected_aa_ref == aa_ref, "get_aminoacid_ref_pos_alt() went wrong"
    assert expected_aa_pos == aa_pos, "get_aminoacid_ref_pos_alt() went wrong"
    assert expected_aa_alt == aa_alt, "get_aminoacid_ref_pos_alt() went wrong"


def test_introduce_mut2cds_case4():
    _, _, row = setup_get_cds_pos_case4()
    seq, expected_seq_mut = setup_introduce_mut2cds_case4()
    cds_pos = 28 - 1
    seq_mut = introduce_mut2cds(row, cds_pos, str(seq.seq))
    assert str(
        expected_seq_mut.seq) == seq_mut, "introduce_mut2seq() went wrong"


# case 5 : inframe insertion, negative strand
def setup_get_cds_pos_case5():
    """
        case 5 = inframe insertion, - strand
        please refer to https://www.ensembl.org/Homo_sapiens/Variation/Explore?db=core;g=ENSG00000055483;r=17:78802461-78840864;t=ENST00000588086;v=rs773813684;vdb=variation;vf=366593845
    """
    exons = {}
    exons[3] = [78836111, 78836363, 0]
    exons[4] = [78835280, 78835501, 2]
    exons[5] = [78828897, 78829007, 2]
    exons[6] = [78827245, 78827347, 2]
    exons[7] = [78821937, 78822004, 1]
    exons[8] = [78820991, 78821061, 2]
    exons[9] = [78819930, 78820012, 0]
    exons[10] = [78818667, 78818778, 1]
    exons[11] = [78814412, 78814552, 0]
    exons[12] = [78813773, 78813873, 0]
    exons[13] = [78812860, 78813001, 1]
    exons[14] = [78806959, 78807636, 0]
    exons[15] = [78806156, 78806286, 0]
    exons[16] = [78803385, 78803978, 1]
    exons[17] = [78802461, 78802535, 1]
    exon_number = 14
    df = pd.DataFrame({
        'chr': [17],
        'ref': ['A'],
        'alt': ['AGTG'],
        'pos': [78807019],
        'strand': ['-']
    })
    row = df.iloc[0]
    return (exons, exon_number, row)


def setup_introduce_mut2cds_case5():
    test_file = "./VCFtoProteogenomics_test_files/cds_ENST00000588086.fasta"
    cds_file = SeqIO.index(test_file, 'fasta')
    return (cds_file['ENST00000588086'],
            cds_file['ENST00000588086_c.2025:T>CACT'])


def test_get_cds_pos_case5():
    expected_cds_pos = 2025 - 1
    exons, exon_number, row = setup_get_cds_pos_case5()
    cds_pos = get_cds_pos(exons, exon_number, row)
    message = "The expected cds_pos {}".format(expected_cds_pos)
    message = message + "doesn't match the calculated on {}".format(cds_pos)
    assert expected_cds_pos == cds_pos, message


def test_get_aminoacid_ref_pos_alt_case5():
    # TODO: reverify the aa_alt for this case
    _, _, row = setup_get_cds_pos_case5()
    seq, seq_mut = setup_introduce_mut2cds_case5()
    cds_pos = 2025 - 1
    expected_aa_ref = "T"
    expected_aa_alt = "T-ins"
    expected_aa_pos = 675
    aa_ref, aa_pos, aa_alt = get_aminoacid_ref_pos_alt(row,
                                                       str(seq.seq),
                                                       str(seq_mut.seq),
                                                       cds_pos,
                                                       to_stop=True)
    assert expected_aa_ref == aa_ref, "get_aminoacid_ref_pos_alt() went wrong"
    assert expected_aa_pos == aa_pos, "get_aminoacid_ref_pos_alt() went wrong"
    assert expected_aa_alt == aa_alt, "get_aminoacid_ref_pos_alt() went wrong"


def test_introduce_mut2cds_case5():
    _, _, row = setup_get_cds_pos_case5()
    seq, expected_seq_mut = setup_introduce_mut2cds_case5()
    cds_pos = 2025 - 1
    seq_mut = introduce_mut2cds(row, cds_pos, str(seq.seq))
    assert str(
        expected_seq_mut.seq) == seq_mut, "introduce_mut2seq() went wrong"


# case 6 : in frame deletion, negative strand
def setup_get_cds_pos_case6():
    """
        case 6 = inframe deletion, negative strand
        please refer to https://www.ensembl.org/Homo_sapiens/Variation/Explore?db=core;g=ENSG00000055483;r=17:78802461-78840864;t=ENST00000588086;v=rs754050981;vdb=variation;vf=365980091
    """
    exons = {}
    exons[3] = [78836111, 78836363, 0]
    exons[4] = [78835280, 78835501, 2]
    exons[5] = [78828897, 78829007, 2]
    exons[6] = [78827245, 78827347, 2]
    exons[7] = [78821937, 78822004, 1]
    exons[8] = [78820991, 78821061, 2]
    exons[9] = [78819930, 78820012, 0]
    exons[10] = [78818667, 78818778, 1]
    exons[11] = [78814412, 78814552, 0]
    exons[12] = [78813773, 78813873, 0]
    exons[13] = [78812860, 78813001, 1]
    exons[14] = [78806959, 78807636, 0]
    exons[15] = [78806156, 78806286, 0]
    exons[16] = [78803385, 78803978, 1]
    exons[17] = [78802461, 78802535, 1]
    exon_number = 5
    df = pd.DataFrame({
        'chr': [17],
        'ref': ['TGAA'],
        'alt': ['T'],
        'pos': [78828912],
        'strand': ['-']
    })
    row = df.iloc[0]
    return (exons, exon_number, row)


def setup_introduce_mut2cds_case6():
    test_file = "./VCFtoProteogenomics_test_files/cds_ENST00000588086.fasta"
    cds_file = SeqIO.index(test_file, 'fasta')
    return (cds_file['ENST00000588086'],
            cds_file['ENST00000588086_c>571:TTCA>A'])


def test_get_cds_pos_case6():
    expected_cds_pos = 571 - 1
    exons, exon_number, row = setup_get_cds_pos_case6()
    cds_pos = get_cds_pos(exons, exon_number, row)
    message = "The expected cds_pos {}".format(expected_cds_pos)
    message = message + "doesn't match the calculated on {}".format(cds_pos)
    assert expected_cds_pos == cds_pos, message


def test_get_aminoacid_ref_pos_alt_case6():
    _, _, row = setup_get_cds_pos_case6()
    seq, seq_mut = setup_introduce_mut2cds_case6()
    cds_pos = 571 - 1
    expected_aa_ref = "F"
    expected_aa_alt = "del"
    expected_aa_pos = 190
    aa_ref, aa_pos, aa_alt = get_aminoacid_ref_pos_alt(row,
                                                       str(seq.seq),
                                                       str(seq_mut.seq),
                                                       cds_pos,
                                                       to_stop=True)
    assert expected_aa_ref == aa_ref, "get_aminoacid_ref_pos_alt() went wrong"
    assert expected_aa_pos == aa_pos, "get_aminoacid_ref_pos_alt() went wrong"
    assert expected_aa_alt == aa_alt, "get_aminoacid_ref_pos_alt() went wrong"


def test_introduce_mut2cds_case6():
    _, _, row = setup_get_cds_pos_case6()
    seq, expected_seq_mut = setup_introduce_mut2cds_case6()
    cds_pos = 571 - 1
    seq_mut = introduce_mut2cds(row, cds_pos, str(seq.seq))
    assert str(
        expected_seq_mut.seq) == seq_mut, "introduce_mut2seq() went wrong"


def test_prepare_vcf():
    test_file = "./VCFtoProteogenomics_test_files/test.vcf"
    pyvcf = prepare_vcf(test_file)
    msg = 'prepare_vcf() didn\'t return a BedTool object'
    assert isinstance(pyvcf, pybedtools.bedtool.BedTool), msg
