import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


def calculate_gc_content(sequence):
    """Calculate the GC content of a sequence as a fraction."""
    gc_count = sequence.count("G") + sequence.count("C")
    return gc_count / len(sequence) if sequence else 0.0


def plot_cov(covs, legend_status=True, nucleotide_status=True, window=75,
             nucleotide_info_version="1_4_0", virus_info=None,
             nucleotide_info=None, unreliable_regions=None, **kwargs):
    """
    Plots the coverage and nucleotide content profile of the mapped plant sample.

    Parameters:
        covs (dict): A dictionary of coverage information for one or more plant samples.
        legend_status (bool): Whether to display the legend. Default is True.
        nucleotide_status (bool): Whether to display nucleotide information. Default is True.
        window (int): Sliding window size. Default is 75.
        nucleotide_info_version (str): Version of nucleotide information. Default is "1_4_0".
        virus_info (dict): Dictionary of virus segments as sequences.
        nucleotide_info (DataFrame): Nucleotide information DataFrame.
        unreliable_regions (DataFrame): DataFrame with unreliable regions information.
        **kwargs: Additional arguments passed to matplotlib plotting functions.

    Returns:
        None: Displays the coverage plots.
    """
    for sample, sample_cov in covs.items():
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        axes = axes.flatten()
        counter = 0

        for seg, cov_values in sample_cov.items():
            ax_cov = axes[counter]
            ax_nucleotide = axes[counter + 1]

            # plot coverage profile
            ax_cov.plot(cov_values, label="Coverage", **kwargs)
            ax_cov.set_title(f"{sample}: {seg} (Coverage)", fontsize=10)
            ax_cov.set_ylabel("Coverage")
            ax_cov.set_xlabel("Position")

            # add unreliable regions
            if unreliable_regions is not None:
                unreliable_seg = unreliable_regions[
                    (unreliable_regions["Virus segment"] == seg) &
                    (unreliable_regions["Categories"].isin(
                        ["Unmappable regions (virus)",
                         "Unmappable regions (host)"]
                    ))
                ]

                for _, row in unreliable_seg.iterrows():
                    start, end = row["Start"], row["End"]
                    ax_cov.axvspan(start, end, color="red", alpha=0.3,
                                   label="Unmappable region")

            # plot nucleotide content
            if nucleotide_status and virus_info is not None:
                seq = virus_info.get(seg, "")
                gc_content = []
                a_content = []

                # sliding window analysis
                for i in range(len(seq) - window + 1):
                    window_seq = seq[i:i + window]
                    gc_content.append(calculate_gc_content(window_seq))
                    a_content.append(window_seq.count("A") / window)

                # overlay nucleotide content
                ax_nucleotide.plot(
                    gc_content, label="GC content", color="black")
                ax_nucleotide.plot(a_content, label="A percentage",
                                   linestyle="--", color="dimgrey")
                ax_nucleotide.set_title(
                    f"{sample}: {seg} (Nucleotide Content)", fontsize=10)
                ax_nucleotide.set_ylim(0, 1)
                ax_nucleotide.set_ylabel("Proportion")
                ax_nucleotide.set_xlabel("Position (sliding window)")

                if legend_status:
                    ax_nucleotide.legend(loc="upper right")

            counter += 2

        plt.tight_layout()
        plt.show()


if __name__ == "__main__":
    # Example usage
    covs = {
        "sample1": {
            "seg1": np.random.randint(0, 100, size=1000),
            "seg2": np.random.randint(0, 100, size=1000)
        }
    }
    virus_info = {"seg1": "ACGT" * 250, "seg2": "TGCA" * 250}
    unreliable_regions = pd.DataFrame({
        "Start": [100, 500],
        "End": [150, 550],
        "Virus segment": ["seg1", "seg2"],
        "Categories": ["Unmappable regions (virus)", "Unmappable regions (host)"]
    })
    nucleotide_info = pd.DataFrame({
        "1_4_0": [True, False],
        "1_5_0": [False, True],
        "seg_id": ["seg1", "seg2"]
    })

    plot_cov(covs, virus_info=virus_info,
             unreliable_regions=unreliable_regions, nucleotide_info=nucleotide_info)
