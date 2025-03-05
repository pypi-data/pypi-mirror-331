===============
PDBNucleicAcids
===============


.. image:: https://img.shields.io/pypi/v/pdbnucleicacids.svg
        :target: https://pypi.python.org/pypi/pdbnucleicacids

.. image:: https://readthedocs.org/projects/pdbnucleicacids/badge/?version=latest
        :target: https://pdbnucleicacids.readthedocs.io/en/latest/?version=latest
        :alt: Documentation Status

.. image:: https://gitlab.com/MorfeoRenai/pdbnucleicacids/badges/main/coverage.svg
        :target: https://gitlab.com/MorfeoRenai/pdbnucleicacids/-/commits/main
        :alt: Coverage Status

.. image:: https://pyup.io/repos/gitlab/MorfeoRenai/pdbnucleicacids/shield.svg
     :target: https://pyup.io/repos/gitlab/MorfeoRenai/pdbnucleicacids/
     :alt: Updates



PDBNucleicAcids is a `Biopython <https://biopython.org/>`_ based package that can parse
all nucleic acids in a PDB structure, with a special focus on
base-pair representation.

* Free software: MIT license
* Documentation: https://pdbnucleicacids.readthedocs.io.


Get Started
-----------

The official release is found in the Python Package Index (PyPI)

.. code-block:: console

    $ pip install pdbnucleicacids

You can parse single stranded and double stranded nucleic acids.

.. code-block:: python

    from Bio.PDB.MMCIFParser import MMCIFParser
    from PDBNucleicAcids.NucleicAcid import DSNABuilder
    
    # parse and build structure with Biopython
    parser = MMCIFParser()
    structure = parser.get_structure(
         structure_id="1A02", filename="1a02-assembly1.cif"
    )
    
    # extract all double strand nucleic acids
    builder = DSNABuilder()
    dsna_list = builder.build_double_strands(structure)
    
    # take the first double strand nucleic acid as an example
    dsna = dsna_list[0]
    
    # extract base-pairs data from double stranded nucleic acid
    df = dsna.get_dataframe()
    df.head()

.. code-block:: console

      i_chain_id  i_residue_index  ... j_residue_index j_chain_id
    0          A             4003  ...            5020          B
    1          A             4004  ...            5019          B
    2          A             4005  ...            5018          B
    3          A             4006  ...            5017          B
    4          A             4007  ...            5016          B

Check the official documentation for more information.


TODO
----

* in ``search_paired_base`` maybe add a scoring function instead of simple distance

* in ``search_paired_base`` add a warning if there is more than one candidate
  or maybe more than one candidate with similar dist or score

* in ``BasePair`` get other information: shear, stretch, buckle, propeller, opening

* explore the ``is_nucleic(non_standard)`` and maybe check if it needs updating

* Proper tests (WIP)


Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
