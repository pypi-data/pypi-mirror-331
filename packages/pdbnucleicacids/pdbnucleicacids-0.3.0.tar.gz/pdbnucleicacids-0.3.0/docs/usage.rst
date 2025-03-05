=====
Usage
=====

To use PDBNucleicAcids in a project:

.. code-block:: python

    import PDBNucleicAcids


Build All Strands of Nucleic Acids
----------------------------------

PDBNucleicAcids can parse all strands of nucleic acids in a Biopython structure.

.. code-block:: python

    from Bio.PDB.PDBList import PDBList
    from Bio.PDB.MMCIFParser import MMCIFParser
    from PDBNucleicAcids.NucleicAcid import NABuilder
    
    # retrive file from PDB using Biopython
    pdbl = PDBList()
    pdbl.retrieve_pdb_file(pdb_code="1A02", pdir=".")
    pdbl.retrieve_assembly_file(pdb_code="1A02", assembly_num=1, pdir=".")
    # ... or else use your own
    
    # parse and build structure with Biopython
    parser = MMCIFParser()
    structure = parser.get_structure(
         structure_id="1A02", filename="1a02-assembly1.cif"
    )
    
    # build all nucleic acids
    builder = NABuilder()
    na_list = builder.build_nucleic_acids(structure)
    na_list

.. code-block:: console

    [<NucleicAcid chain='A' type='DNA' start=4001 end=4020>,
     <NucleicAcid chain='B' type='DNA' start=5001 end=5020>]

Every nucleic acid is like a Python list:

.. code-block:: python

    na = na_list[0]
    na[:5]

.. code-block:: console

    [<Residue DT het=  resseq=4001 icode= >,
     <Residue DT het=  resseq=4002 icode= >,
     <Residue DG het=  resseq=4003 icode= >,
     <Residue DG het=  resseq=4004 icode= >,
     <Residue DA het=  resseq=4005 icode= >]

PDBNucleicAcids can get a nucleic acid sequence:

.. code-block:: python

    na.get_seq()

.. code-block:: console

    Seq('TTGGAAAATTTGTTTCATAG')

PDBNucleicAcids can also get a nucleic acid chain id, nucleic acid type and
all atoms:

.. code-block:: python

    print(na.get_chain_id(), na.get_na_type())
    print(na.get_atoms()[:5])

.. code-block:: console

    A DNA
    [<Atom O5'>, <Atom C5'>, <Atom C4'>, <Atom O4'>, <Atom C3'>]


Build All Double-Stranded Nucleic Acids
---------------------------------------

PDBNucleicAcids can parse all double-stranded nucleic acids in a Biopython
structure.

.. code-block:: python

    from PDBNucleicAcids.NucleicAcid import DSNABuilder

    builder = DSNABuilder()
    dsna_list = builder.build_double_strands(structure)
    dsna_list

.. code-block:: console

    [<DoubleStrandNucleicAcid type='dsDNA' i-th strand='A'
     j-th strand='B' length=17>]


Get All Base-Pairs
------------------

PDBNucleicAcids can extract all base-pairs object in a double-stranded nucleic
acid. Double straded nucleic acids are like a list of base-pairs:

.. code-block:: python

    dsna = dsna_list[0]
    dsna[:5]

.. code-block:: console

    [<BasePair i_res=DG j_res=DC>,
     <BasePair i_res=DG j_res=DC>,
     <BasePair i_res=DA j_res=DT>,
     <BasePair i_res=DA j_res=DT>,
     <BasePair i_res=DA j_res=DT>]

PDBNucleicAcids can extract all base-pairs data in a double-stranded
nucleic acid.

.. code-block:: python

    dsna = dsna_list[0]
    df = dsna.get_dataframe()
    df.head()

.. code-block:: console

      i_chain_id  i_residue_index  ... j_residue_index j_chain_id
    0          A             4003  ...            5020          B
    1          A             4004  ...            5019          B
    2          A             4005  ...            5018          B
    3          A             4006  ...            5017          B
    4          A             4007  ...            5016          B


Search Individual Pair Bases
----------------------------

PDBNucleicAcids can search for paired nucleotide, given an input nucleotide.

.. code-block:: python

    from PDBNucleicAcids.NucleicAcid import search_paired_base
    
    # input nucleotide
    base = structure[0]["A"][4003]  # DG
    
    # search for paired nucleotide
    paired_base = search_paired_base(base)
    paired_base

.. code-block:: console

    <Residue DC het=  resseq=5020 icode= >

PDBNucleicAcids will recognize unpaired bases.

.. code-block:: python

    # input nucleotide
    base = structure[0]["A"][4001]  # DT
    
    # search for paired nucleotide
    paired_base = search_paired_base(base)
    print(paired_base)

.. code-block:: console

    None


DNA-RNA Complexes
-----------------

PDBNucleicAcids base-pairing can be used for DNA-RNA base-pairs.

.. code-block:: python

    from Bio.PDB.PDBList import PDBList
    from Bio.PDB.MMCIFParser import MMCIFParser
    from PDBNucleicAcids.NucleicAcid import search_paired_base

    # retrive file from PDB using Biopython
    pdbl = PDBList()
    pdbl.retrieve_assembly_file(pdb_code="9K7R", assembly_num=1, pdir=".")

    # parse and build structure with Biopython
    parser = MMCIFParser()
    structure = parser.get_structure(
         structure_id="9K7R", filename="9k7r-assembly1.cif"
    )
    
    # input nucleotide
    base = structure[0]["B"][8]  # DT

    # search for paired nucleotide
    paired_base = search_paired_base(base)
    
    # paired base is RNA base
    paired_base

.. code-block:: console

    <Residue A het=  resseq=2 icode= >


Custom Rules for Base-Pairing
-----------------------------

PDBNucleicAcids base-pairing can be expanded, by changing parameters used in the
base-pairing rules.

.. code-block:: python

    from PDBNucleicAcids.BasePairRules import dsDNAWatsonCrickBasePairRules
    
    parser = MMCIFParser()
    structure = parser.get_structure(
         structure_id="1A02", filename="1a02-assembly1.cif"
    )
    
    # custom base pairing rules
    my_rules = dsDNAWatsonCrickBasePairRules(
        max_distance = 3.5,
        max_angle = 60,
        max_stagger = 2.0,
    )
    
    # input nucleotide
    base = structure[0]["A"][4003]  # DG
    
    # search for paired nucleotide
    paired_base = search_paired_base(base, pairing_rules=my_rules)


PDBNucleicAcids base-pairing can be expanded even further by creating your own
base-pairing rules.


.. code-block:: python

    from PDBNucleicAcids.BasePairRules import WatsonCrickBasePairRules
    
    parser = MMCIFParser()
    structure = parser.get_structure(
         structure_id="1A02", filename="1a02-assembly1.cif"
    )
    
    # input nucleotide
    base = structure[0]["A"][1]  # G
    
    # search for paired nucleotide with default rules
    pairing_rules = WatsonCrickBasePairRules()
    paired_base = search_paired_base(base, pairing_rules=pairing_rules)
    # this returns None because it binds a non-standard DNA base: 5CM
    
    # to circumvent this we can code our own rules
    class MyRules(WatsonCrickBasePairRules):
        def __init__(self):
            super().__init__()
            
            self.complementary_pairs += [("5CM", "G"), ("G", "5CM")]
            
            self.pyrimidines.append("5CM")
            
            self.accepted_nucleotides.append("5CM")
    
    # search for paired nucleotide with custom base pairing rules
    pairing_rules = MyRules()
    paired_base = search_paired_base(base, pairing_rules=pairing_rules)
    paired_base

.. code-block:: console

    <Residue 5CM het=H_5CM resseq=9 icode= >


Limitations
-----------

PDBNucleicAcids doesn't support yet recognition of flipped bases,
gaps and nicks.
