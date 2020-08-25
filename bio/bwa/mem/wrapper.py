__author__ = "Johannes Köster, Julian de Ruiter"
__copyright__ = "Copyright 2016, Johannes Köster and Julian de Ruiter"
__email__ = "koester@jimmy.harvard.edu, julianderuiter@gmail.com"
__license__ = "MIT"


import os
from os import path


# Extract arguments.
extra = snakemake.params.get("extra", "")

sort = snakemake.params.get("sort", "none")
sort_order = snakemake.params.get("sort_order", "coordinate")
sort_extra = snakemake.params.get("sort_extra", "")

log = snakemake.log_fmt_shell(stdout=False, stderr=True)

# Check inputs/arguments.
if not isinstance(snakemake.input.reads, str) and len(snakemake.input.reads) not in {
    1,
    2,
}:
    raise ValueError("input must have 1 (single-end) or " "2 (paired-end) elements")

if sort_order not in {"coordinate", "queryname"}:
    raise ValueError("Unexpected value for sort_order ({})".format(sort_order))

# Determine which pipe command to use for converting to bam or sorting.
if sort == "none":

    # Simply convert to bam using samtools view.
    pipe_cmd = f"samtools view -Sbh -o {snakemake.output[0]} -"

elif sort == "samtools":

    # Sort alignments using samtools sort.
    pipe_cmd = f"samtools sort {sort_extra} -o {snakemake.output[0]} -"

    # Add name flag if needed.
    if sort_order == "queryname":
        sort_extra += " -n"

    prefix = path.splitext(snakemake.output[0])[0]
    sort_extra += " -T " + prefix + ".tmp"

elif sort == "picard":

    # Sort alignments using picard SortSam.
    pipe_cmd = (
        f"picard SortSam {sort_extra} INPUT=/dev/stdin"
        f" OUTPUT={snakemake.output[0]} SORT_ORDER={sort_order}"
    )

else:
    raise ValueError("Unexpected value for params.sort ({})".format(sort))

os.system(
    f"(bwa mem"
    f" -t {snakemake.threads}"
    f" {extra}"
    f" {snakemake.params.index}"
    f" {snakemake.input.reads}"
    f" | " + pipe_cmd + f") {log}"
)
