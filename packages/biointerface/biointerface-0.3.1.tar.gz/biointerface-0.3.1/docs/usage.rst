=====
Usage
=====

To use BioInterface in a Python project:

.. code-block:: python

    import biointerface


Extract One Protein-DNA Interface
---------------------------------

You can extract a single Protein-DNA interface from a single protein chain.

.. code-block:: python

    from Bio.PDB.PDBList import PDBList
    from Bio.PDB.MMCIFParser import MMCIFParser
    from biointerface import Interface

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

    # extract interface from a specific protein chain
    face = Interface(
        structure=structure,
        protein_chain_id="F",
        search_radius=5.0
    )
    face


.. code-block:: console

    <Interface chains=F:BA contacts=258 search_radius=5.0>


Extract All Protein-DNA Interfaces
----------------------------------

You can also extract all Protein-DNA interface from an entire structure.

.. code-block:: python

    from biointerface import build_interfaces

    face_list = build_interfaces(structure=structure, search_radius=5.0)
    face_list

.. code-block:: console

    [<Interface chains=J:BA contacts=189 search_radius=5.0>,
     <Interface chains=F:BA contacts=258 search_radius=5.0>,
     <Interface chains=N:BA contacts=529 search_radius=5.0>]


Get All Interacting Residues
----------------------------

You can access all interacting residues in a Protein-DNA interface, both
aminoacids and nucleotides.

.. code-block:: python

    face.get_aminoacids()

.. code-block:: console

    [<Residue ARG het=  resseq=144 icode= >,
     <Residue ALA het=  resseq=151 icode= >,
     <Residue ARG het=  resseq=158 icode= >,
     <Residue ASN het=  resseq=147 icode= >,
     <Residue LYS het=  resseq=148 icode= >,
     <Residue LYS het=  resseq=153 icode= >,
     <Residue SER het=  resseq=154 icode= >,
     <Residue ARG het=  resseq=155 icode= >,
     <Residue ALA het=  resseq=150 icode= >,
     <Residue ARG het=  resseq=143 icode= >,
     <Residue ARG het=  resseq=146 icode= >,
     <Residue ARG het=  resseq=157 icode= >]

.. code-block:: python

    face.get_nucleotides()

.. code-block:: console

    [<Residue DT het=  resseq=4015 icode= >,
     <Residue DC het=  resseq=4016 icode= >,
     <Residue DT het=  resseq=4014 icode= >,
     <Residue DG het=  resseq=5007 icode= >,
     <Residue DA het=  resseq=4017 icode= >,
     <Residue DT het=  resseq=4018 icode= >,
     <Residue DT het=  resseq=5006 icode= >,
     <Residue DC het=  resseq=5003 icode= >,
     <Residue DA het=  resseq=5005 icode= >,
     <Residue DG het=  resseq=4012 icode= >,
     <Residue DT het=  resseq=4013 icode= >,
     <Residue DT het=  resseq=5004 icode= >]


Get All Interacting Atoms
-------------------------

You can access all interacting atoms in a Protein-DNA interface.

First of all you can get all interacting atoms as atom pairs.

.. code-block:: python

    contacts = face.get_atomic_contacts()
    contacts[:5]

.. code-block:: console

    [(<Atom C5'>, <Atom NZ>),
     (<Atom C5'>, <Atom CE>),
     (<Atom O5'>, <Atom NZ>),
     (<Atom O5'>, <Atom CE>),
     (<Atom O5'>, <Atom CD>)]

You can also get all Protein or DNA interacting atoms, independently.

.. code-block:: python

    atoms = face.get_protein_atoms()
    atoms[:5]

.. code-block:: console

    [<Atom CZ>, <Atom N>, <Atom NE>, <Atom CD>, <Atom CG>]

.. code-block:: python

    atoms = face.get_dna_atoms()
    atoms[:5]

.. code-block:: console

    [<Atom P>, <Atom C5'>, <Atom C6>, <Atom C5>, <Atom C4'>]


Interface Data as DataFrame
---------------------------

You can get all Protein-DNA interface features as a ``pandas`` DataFrame.

.. code-block:: python

    df = face.get_interface_data()
    df.columns

.. code-block:: console

    Index(['protein_chain_id', 'prot_res_hetfield', 'prot_res_number',
       'prot_res_icode', 'prot_res_name', 'prot_atom_name', 'prot_atom_altloc',
       'prot_atom_element', 'prot_atom_coord_x', 'prot_atom_coord_y',
       'prot_atom_coord_z', 'dna_chain_id', 'dna_res_hetfield',
       'dna_res_number', 'dna_res_icode', 'dna_res_name', 'dna_atom_name',
       'dna_atom_altloc', 'dna_atom_element', 'dna_atom_coord_x',
       'dna_atom_coord_y', 'dna_atom_coord_z', 'euclidean_distance'],
      dtype='object')

.. code-block:: python

    df

.. code-block:: console

        protein_chain_id prot_res_hetfield  prot_res_number  ... euclidean_distance
    0                  F                                148  ...           4.458498
    1                  F                                148  ...           3.964944
    2                  F                                148  ...           4.066739
    3                  F                                148  ...           3.271817
    4                  F                                148  ...           4.217340
    ...              ...               ...              ...  ...                ...
    253                F                                154  ...           4.644194
    254                F                                150  ...           4.594888
    255                F                                150  ...           4.784895
    256                F                                157  ...           4.904832
    257                F                                157  ...           4.299844

    [258 rows x 23 columns]


Protein-Bound Nucleic Acids
---------------------------

BioInterface can extract all double-strand nucleic acids bound by
the input protein, as a ``DoubleStrandNucleicAcid`` class from the package
PDBNucleicAcids_.

.. code-block:: python

    bound_dsna_list = face.get_bound_double_strands()
    bound_dsna = dsna_list[0]
    bound_dsna

.. code-block:: console

    <DoubleStrandNucleicAcid type='dsDNA' i-th strand='A' j-th strand='B'
     length=9>

The ``DoubleStrandNucleicAcid`` class has other useful methods.

.. code-block:: python

    bound_dsna.get_i_strand().get_seq()

.. code-block:: console

    Seq('GTTTCATAG')

.. _PDBNucleicAcids: https://gitlab.com/MorfeoRenai/pdbnucleicacids
