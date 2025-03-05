"""
A (very) small package for generating
[PGFinder](https://github.com/Mesnage-Org/pgfinder)-compatible glycopeptide
databases.

Just supply a FASTA file containing the protein(s) of interest,
specify the digestion parameters, a glycosylation motif, and a list of potential
glycan compositions / structures.

# INCLUDE A SHORT CODE EXAMPLE HERE!
We can include a markdown file that shows how to use the web interface /
whatever other documentation seems useful!
```py
print("Test?")
```
"""

# Imports ======================================================================

# Standard Library
from io import StringIO
from typing import Iterable, Pattern

# Dependencies
from pyteomics.fasta import Protein
import pyteomics.fasta

# Local Modules
from glam._lib import (
    load_glycans,
    digest_protein,
    modify_peptides,
    filter_glycopeptides,
    peptide_masses,
    build_glycopeptides,
    convert_to_csv,
)

# Constants ====================================================================

DIGESTIONS: dict[str, str] = {
    "Arg-C Endopeptidase": r"R",
    "Asp-N Endopeptidase": r"\w(?=D)",
    "BNPS-Skatole": r"W",
    "Caspase-1": r"(?<=[FWYL]\w[HAT])D(?=[^PEDQKR])",
    "Caspase-2": r"(?<=DVA)D(?=[^PEDQKR])",
    "Caspase-3": r"(?<=DMQ)D(?=[^PEDQKR])",
    "Caspase-4": r"(?<=LEV)D(?=[^PEDQKR])",
    "Caspase-5": r"(?<=[LW]EH)D",
    "Caspase-6": r"(?<=VE[HI])D(?=[^PEDQKR])",
    "Caspase-7": r"(?<=DEV)D(?=[^PEDQKR])",
    "Caspase-8": r"(?<=[IL]ET)D(?=[^PEDQKR])",
    "Caspase-9": r"(?<=LEH)D",
    "Caspase-10": r"(?<=IEA)D",
    "Chymotrypsin (High Specificity)": r"([FY](?=[^P]))|(W(?=[^MP]))",
    "Chymotrypsin (Low Specificity)": r"([FLY](?=[^P]))|(W(?=[^MP]))|(M(?=[^PY]))|(H(?=[^DMPW]))",
    "Clostripain": r"R",
    "CNBr": r"M",
    "Enterokinase": r"(?<=[DE]{3})K",
    "Factor Xa": r"(?<=[AFGILTVM][DE]G)R",
    "Formic Acid": r"D",
    "Glutamyl Endopeptidase": r"E",
    "Granzyme B": r"(?<=IEP)D",
    "Hydroxylamine": r"N(?=G)",
    "Iodosobenzoic Acid": r"W",
    "LysC": r"K",
    "2-Nitro-5-Thiocyanatobenzoic Acid": r"\w(?=C)",
    "Pepsin (pH 1.3)": r"((?<=[^HKR][^P])[^R](?=[FL][^P]))|((?<=[^HKR][^P])[FL](?=\w[^P]))",
    "Pepsin (pH 2.0)": r"((?<=[^HKR][^P])[^R](?=[FLWY][^P]))|((?<=[^HKR][^P])[FLWY](?=\w[^P]))",
    "Proline Endopeptidase": r"(?<=[HKR])P(?=[^P])",
    "Proteinase K": r"[AEFILTVWY]",
    "Staphylococcal Peptidase I": r"(?<=[^E])E",
    "Thermolysin": r"[^DE](?=[AFILMV][^P])",
    "Thrombin": r"((?<=G)R(?=G))|((?<=[AFGILTVM][AFGILTVWA]P)R(?=[^DE][^DE]))",
    "Trypsin": r"([KR](?=[^P]))|((?<=W)K(?=P))|((?<=M)R(?=P))",
}
"""
A dictionary mapping common protein digestion treatments to the regular expressions
that describe their cleavage sites.  
"""

GLYCOSYLATION_MOTIFS: dict[str, str] = {"N": r"N[^P][TS]"}
"""
A dictionary mapping common glycosylation types to regular expressions that
describe the sequence motifs they target.
"""

MODIFICATIONS: dict[str, tuple[str, list[str], float]] = {
    "Methionine Oxidation": ("ox", ["M"], 15.994915),
    "Carbamidomethyl": ("cm", ["C"], 57.021464),
    "N-Deamidation": ("da", ["N"], 0.984016),
}
# FIXME: Write the docstring for this!
# FIXME: Ask Caroline what to call these?

# Functions ====================================================================


# FIXME: This docstring is still out of date / wrong!
def generate_glycopeptides(
    fasta: str,
    # FIXME: No clue what to call this...
    digestion: str | Pattern[str],
    motif: str | Pattern[str],
    glycans: str,
    modifications: Iterable[tuple[str, list[str], float]] = [],
    max_modifications: int | None = None,
    missed_cleavages: int = 0,
    min_length: int | None = None,
    max_length: int | None = None,
    semi_enzymatic: bool = False,
    all_peptides: bool = False,
    **kwargs,
) -> list[tuple[str, str]]:
    """Generates glycopeptides from an input FASTA and CSV file of glycans.

    Parameters
    ----------
    fasta : str,
        FASTA text describing the protein sequence(s) to be digested. Note that this
        function ***does not*** read from the filesystem — you'll need to first load
        your FASTA file into a `str` using something like `pathlib.Path.read_text`.
    enzyme : str or Pattern[str],
        The name of the enyzme used to digest the protein into peptides. A number of
        enzymes are built-in (see `pyteomics.parser.expasy_rules` and
        `pyteomics.parser.psims_rules`), but a custom (optionally pre-compiled)
        regex describing the enzyme's cleavage site can also be supplied. For more
        information, see `pyteomics`'s documentation.
    motif : str or Pattern[str],
        A regex describing the sequence motif for glycosylation. Only peptides
        containing this motif will be used to generate the final list of glycopeptides.
        See the `glam.GLYCOSYLATION_MOTIFS` dictionary for common motifs.
    glycans : str,

    missed_cleavages : int, default: 0,
        The maximum number of missed cleavages to allow during digestion
    min_length : int or None, default: None,
        The minimum length peptide to include in the digest output
    max_length : int or None, default: None,
        The maximum length peptide to include in the digest output
    semi : bool, default: False,
    """

    proteins = pyteomics.fasta.read(StringIO(fasta), use_index=False)
    potential_glycans = load_glycans(glycans)

    def generate(protein: Protein) -> tuple[str, str]:
        filename = f"{protein.description}.csv"
        seq = protein.sequence

        peptides = digest_protein(
            seq, digestion, missed_cleavages, min_length, max_length, semi_enzymatic
        )
        modified_peptides = modify_peptides(peptides, modifications, max_modifications)
        motif_peptides = filter_glycopeptides(modified_peptides, motif)
        motif_peptide_masses = peptide_masses(motif_peptides, modifications)
        glycopeptides = build_glycopeptides(motif_peptide_masses, potential_glycans)

        if all_peptides:
            glycopeptides |= peptide_masses(modified_peptides, modifications)

        csv = convert_to_csv(glycopeptides)
        return (filename, csv)

    return [generate(protein) for protein in proteins]
