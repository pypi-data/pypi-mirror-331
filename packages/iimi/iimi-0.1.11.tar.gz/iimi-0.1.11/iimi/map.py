import os
import pysam
import pandas as pd


def create_high_nucleotide_content(gc=0.6, a=0.45, window=75, virus_info=None):
    """
    create_high_nucleotide_content(gc=0.6, a=0.45, window=75, virus_info=None)

    Creates a DataFrame of start and end positions for regions with high GC% and A% content.

    Parameters:
        gc (float): Threshold for GC content. Default is 0.6.
        a (float): Threshold for A nucleotide proportion. Default is 0.45.
        window (int): Sliding window size. Default is 75.
        virus_info (dict): Dictionary of virus sequences. Keys are segment IDs, values are sequences.

    Returns:
        pd.DataFrame: DataFrame with columns ['Start', 'End', 'Virus segment', 'Categories'].
    """
    unreliable_regions = []

    for segment, seq in virus_info.items():
        seq_length = len(seq)
        gc_seq = [
            (seq[i:i+window].count('G') + seq[i:i+window].count('C')) / window
            for i in range(seq_length - window + 1)
        ]
        a_seq = [
            seq[i:i+window].count('A') / window
            for i in range(seq_length - window + 1)
        ]

        # find high GC regions
        regions_gc = [0] * seq_length
        for i, val in enumerate(gc_seq):
            if val > gc:
                regions_gc[i:i+window] = [1] * window
        region_gc_index = intervals_from_positions(
            [i for i, val in enumerate(regions_gc) if val == 1])

        for start, end in region_gc_index:
            unreliable_regions.append((start, end, segment, "CG% > 60%"))

        # find high A regions
        regions_a = [0] * seq_length
        for i, val in enumerate(a_seq):
            if val > a:
                regions_a[i:i+window] = [1] * window
        region_a_index = intervals_from_positions(
            [i for i, val in enumerate(regions_a) if val == 1])

        for start, end in region_a_index:
            unreliable_regions.append((start, end, segment, "A% > 45%"))

    unreliable_regions_df = pd.DataFrame(unreliable_regions, columns=[
                                         "Start", "End", "Virus segment", "Categories"])
    return unreliable_regions_df


def intervals_from_positions(positions):
    """
    Converts a list of positions into intervals.

    Parameters:
        positions (list): List of positions.

    Returns:
        list: List of (start, end) intervals.
    """
    if not positions:
        return []

    intervals = []
    start = positions[0]
    for i in range(1, len(positions)):
        if positions[i] != positions[i - 1] + 1:
            intervals.append((start, positions[i - 1]))
            start = positions[i]
    intervals.append((start, positions[-1]))
    return intervals


def create_mappability_profile(path_to_bam_files,
                               category="Unmappable regions", window=75, virus_info=None):
    """
    create_mappability_profile(path_to_bam_files,
                               category="Unmappable regions", window=75, virus_info=None)

    Creates a DataFrame of start and end positions for unmappable regions.

    Parameters:
        path_to_bam_files (str): Path to folder containing sorted BAM files.
        category (str): Category for the unreliable regions. Default is "Unmappable regions".
        window (int): Sliding window size. Default is 75.
        virus_info (dict): Dictionary of virus sequences. Keys are segment IDs, values are sequences.

    Returns:
        pd.DataFrame: DataFrame with columns ['Start', 'End', 'Virus segment', 'Categories'].
    """
    if virus_info is None or not isinstance(virus_info, dict):
        raise ValueError(
            "virus_info must be a dictionary with segment IDs as keys and sequences as values.")

    bam_files = [
        os.path.join(path_to_bam_files, f) for f in os.listdir(path_to_bam_files)
        if f.endswith(".sorted.bam")
    ]
    unreliable_regions = []

    for bam_file in bam_files:
        bam = pysam.AlignmentFile(bam_file, "rb")
        segment_id = os.path.basename(bam_file).split(".")[0]
        seq = virus_info.get(segment_id)

        if seq is None:
            print("Segment ID " + segment_id +
                  " not found in virus_info. Skipping.")
            continue

        seq_length = len(seq)
        regions = [0] * seq_length

        for read in bam.fetch():
            start = read.reference_start
            end = start + window
            for i in range(start, min(end, seq_length)):
                regions[i] = 1

        region_index = intervals_from_positions(
            [i for i, val in enumerate(regions) if val == 1])

        for start, end in region_index:
            unreliable_regions.append((start, end, segment_id, category))

    unreliable_regions_df = pd.DataFrame(unreliable_regions, columns=[
                                         "Start", "End", "Virus segment", "Categories"])
    return unreliable_regions_df
