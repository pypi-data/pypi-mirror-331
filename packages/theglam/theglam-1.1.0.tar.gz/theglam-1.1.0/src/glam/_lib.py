# Imports ==============================================================================

# Standard Library
from io import StringIO
from typing import Iterable, Pattern
import csv
import itertools
import re

# Dependencies
from pyteomics.auxiliary import PyteomicsError
import glycowork.motif.tokenization as glycowork
import pyteomics.mass
import pyteomics.parser

# Constants ============================================================================

# NOTE: Not quite the monoisotopic water mass that the most accurate mass calculators
# produce, but it is what `glycowork` seems to be using
WATER_MASS: float = 18.0105546

# Functions ============================================================================


def glycan_mass(glycan: str) -> float:
    mass = 0.0

    # Try to parse the string as a fully-defined structure first
    try:
        mass = glycowork.glycan_to_mass(glycan)
    except KeyError:
        # But if that fails, then try just parsing it as a sugar composition
        try:
            mass = glycowork.composition_to_mass(glycan)
        except IndexError:
            pass

    # NOTE: Many nonsense structures / compositions just return the mass of water — if
    # the result was just a water mass, then whatever we were given wasn't valid, so
    # throw an error as if `mass` were never set
    if mass in [0, WATER_MASS]:
        raise ValueError(f"Invalid glycan structure / composition: '{glycan}'")
    else:
        return mass


def load_glycans(glycan_csv: str) -> set[tuple[str, float]]:
    expected_cols = ["Glycan", "Monoisotopic Mass"]

    try:
        rows = csv.reader(StringIO(glycan_csv))
    except Exception as e:
        raise ValueError(f"Failed to read glycan CSV: {e}")

    header = next(rows)

    if header == expected_cols:
        return {(g, float(m)) for g, m in rows}
    elif header == expected_cols[:1]:
        return {(g, glycan_mass(g)) for (g,) in rows}
    else:
        raise ValueError(
            "The glycan file must contain either the columns "
            f"{expected_cols} or just {expected_cols[:1]}"
        )


def digest_protein(
    seq: str,
    rule: str | Pattern[str],
    missed_cleavages: int,
    min_length: int | None,
    max_length: int | None,
    semi_enzymatic: bool,
) -> set[str]:
    return pyteomics.parser.cleave(
        seq, rule, missed_cleavages, min_length, max_length, semi_enzymatic, None, True
    )


def modify_peptides(
    peptides: set[str],
    mods: Iterable[tuple[str, list[str], float]],
    max_mods: int | None = None,
) -> set[str]:
    variable_mods = {n: ts for (n, ts, _) in mods}
    return {
        isoform
        for peptide in peptides
        for isoform in pyteomics.parser.isoforms(peptide, variable_mods=variable_mods)
    }


def filter_glycopeptides(
    peptides: set[str], glycosylation_motif: str | Pattern[str]
) -> set[str]:
    return {p for p in peptides if re.search(glycosylation_motif, p)}


def peptide_masses(
    peptides: set[str], mods: Iterable[tuple[str, list[str], float]] = []
) -> set[tuple[str, float]]:
    def mass(peptide: str) -> float:
        mod_masses = {n: m for (n, _, m) in mods}
        aa_mass = pyteomics.mass.std_aa_mass | mod_masses
        try:
            return pyteomics.mass.fast_mass2(peptide, aa_mass=aa_mass)
        except PyteomicsError as e:
            raise ValueError(
                f"Unknown amino acid residue found in '{peptide}': {e.message}"
            )

    return {(p, mass(p)) for p in peptides}


def build_glycopeptides(
    peptides: set[tuple[str, float]], glycans: set[tuple[str, float]]
) -> set[tuple[str, float]]:
    def build(
        peptide: tuple[str, float], glycan: tuple[str, float]
    ) -> tuple[str, float]:
        peptide_name, peptide_mass = peptide
        glycan_name, glycan_mass = glycan
        name = f"{glycan_name}-{peptide_name}"
        # This is a condensation reaction, so remember to take away a water mass
        mass = glycan_mass + peptide_mass - WATER_MASS
        return (name, mass)

    return {build(p, g) for p, g in itertools.product(peptides, glycans)}


def convert_to_csv(glycopeptides: set[tuple[str, float]]) -> str:
    csv_str = StringIO()
    writer = csv.writer(csv_str)
    writer.writerow(["Structure", "Monoisotopic Mass"])

    sorted_glycopeptides = sorted(
        (("-" in name, mass, name) for name, mass in glycopeptides), reverse=True
    )

    for _, mass, name in sorted_glycopeptides:
        mass = round(mass, 6)
        # NOTE: This is a nasty hack for PGFinder, which expects a `|1` type suffix
        # after the name of each structure. Really, that's a design flaw in PGFinder,
        # but we'll fix it here for now...
        hacky_name = f"{name}|1"
        writer.writerow([hacky_name, mass])

    return csv_str.getvalue()
