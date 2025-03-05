# iimi: identifying infection with machine intelligence

`iimi` is a python package for plant virus diagnostics using high-throughput genome sequencing data. It provides tools for converting BAM files into coverage profiles, processing and visualizing genomic data with handling for unreliable regions, and training machine learning models to predict viral infections.

## Installation

```bash
pip install iimi
```

## Usage

```python
import iimi
```

## Data Processing and Coverage Profile Generation

To convert the indexed and sorted BAM file(s) into coverage profiles and feature-extracted data frame. The coverage profiles will be used to visualize the mapping information. The feature-extracted data frame will be used in the model training and predictions.

```python
# convert BAM files to coverage profiles
bam_files = ["path/to/sample1.sorted.bam", "path/to/sample2.sorted.bam"]
iimi.convert_bam_to_rle(bam_files)

# convert coverage profiles to a feature-extracted DataFrame
rle_data = {
    "sample1": {"seg1": [1, 2, 3, 0, 0, 4], "seg2": [0, 0, 0, 1, 1, 2]},
    "sample2": {"seg3": [2, 3, 4, 5, 0, 1]},
}

additional_info = pd.DataFrame({
    "virus_name": ["Virus4"],
    "iso_id": ["Iso4"],
    "seg_id": ["seg4"],
    "A_percent": [40],
    "C_percent": [20],
    "T_percent": [20],
    "GC_percent": [20],
    "seg_len": [800],
})

iimi.convert_rle_to_df(rle_data, additional_nucleotide_info=additional_info)
```

## Handling Unreliable Regions

Unreliable regions contain high nucleotide content regions and have a mappability profile. Identifying these regions helps eliminate false peaks.

### High Nucleotide Content Regions

High nucleotide content regions is a profile of areas on a virus genome that has high GC content and/or high A nucleotide percentage.

```python
virus_info = {
    "seg1": "ATGCGATCGATCGATCGTACGATCGATCGATCGATCGTACGATCG",
    "seg2": "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
}

# identify regions with high GC content
create_high_nucleotide_content(
    gc=0.4, a=0.0, window=10, virus_info=virus_info
)
# identify regions with high A content
create_high_nucleotide_content(
    gc=0.0, a=0.8, window=10, virus_info=virus_info
)
```

### Mappability Profile

Mappability profile is a profile of areas on a virus genome that can be mapped to other viruses or host genome. This tool uses Arabidopsis Thaliana as the host genome.

```python
# generate mappability profile from host or virus BAM files
create_mappability_profile(
    path_to_bam_files="path/to/bam/files",
    virus_info=virus_info,
    window=10
)
```

## Machine Learning Models to Predict Viral Infections

### Using Pre-trained Models

To use a provided model, input your data to newdata and choose a method: `xgb`, `en`, and `rf`, which stand for pre-trained XGBoost, elastic net, and random forest models. The prediction is `TRUE` if virus infected the sample, `FALSE` if virus did not infect the sample.

```python
# predict using pre-trained random forest model
predict_iimi(newdata=df, method="rf")
```

### Training a Custom Model

The `train_iimi()` function trains a machine learning model on the provided feature-extracted data frame of plant sample (`train_x`) and known target labels (`train_y`). It supports also three models: `xgb`, `en`, and `rf`.

```python
# train random forest model
train_iimi(train_x, train_y, method="rf", ntree=100, mtry=2)
# train XGBoost model
train_iimi(train_x, train_y, method="xgb", nrounds=100)
# train elastic net model
en_model = train_iimi(train_x, train_y, method="en", k=5)
```

## Visualizing Coverage Profiles

`plot_cov()` plots the coverage profile of the mapped plant sample and the percentage of A nucleotides and GC content for a sliding window of k-mer with the default step being 75 bases.

```python
covs = {
    "sample1": {
        "seg1": [20, 30, 50, 60, 80],
        "seg2": [15, 25, 45, 55, 75],
    }
}
virus_info = {
    "seg1": "ACGT" * 250,
    "seg2": "TGCA" * 250,
}

# plot coverage of segments without unreliable regions
plot_cov(
    covs,
    legend_status=True,
    nucleotide_status=True,
    virus_info=virus_info,
    unreliable_regions=None,
)
```

## Sample Data and Models Provided

- `iimi/data/example_cov.pkl` Coverage profiles of three plant samples: A list of coverage profiles for three plant samples
- `iimi/data/example_diag.pdl` Known diagnostics result of virus segments: A matrix containing the known truth about the diagnostics result (using virus database version 1.4.0) for each plant sample for the example data
- `iimi/data/nucleotide_info.pkl` Nucleotide information of virus segments: A data set containing the GC content and other information about the virus segments from the official Virtool virus data base (version 1.4.0)
- `iimi/data/unreliable_regions.pkl` The unreliable regions of the virus segments: A data frame of unmappable regions and regions of CG% and A% over 60% and 45% respectively
for the virus segments
- `iimi/data/trained_rf.pkl` A trained model using the default Random Forest settings
- `iimi/data/trained_xgb.model` A trained model using the default XGBoost settings
- `iimi/data/trained_en.pkl` A trained model using the default Elastic Net settings

## References

- H. Ning, I. Boyes, Ibrahim Numanagić, M. Rott, L. Xing, and X. Zhang, “Diagnostics of viral infections using high-throughput genome sequencing data,” Briefings in Bioinformatics, vol. 25, no. 6, Sep. 2024, doi: https://doi.org/10.1093/bib/bbae501.
- Grigorii Sukhorukov, M. Khalili, Olivier Gascuel, Thierry Candresse, Armelle Marais-Colombel, and Macha Nikolski, “VirHunter: A Deep Learning-Based Method for Detection of Novel RNA Viruses in Plant Sequencing Data,” Frontiers in bioinformatics, vol. 2, May 2022, doi: https://doi.org/10.3389/fbinf.2022.867111.
