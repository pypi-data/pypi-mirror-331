# Orphanet Explorer

A Python package for processing and merging Orphanet XML data files. This package provides tools to extract, transform, and combine data from various Orphanet XML files into a unified dataset.

## Features

- Process multiple Orphanet XML file types
- Extract phenotype, functional consequences, natural history, and epidemiological data
- Merge datasets with intelligent handling of common columns
- Type-safe operations with comprehensive error handling
- Configurable output formats and locations

## Installation

```bash
pip install orphanet_explorer
```

You can download data from https://www.orphadata.com/orphanet-scientific-knowledge-files/

## Quick Start

```python
from orphanet_explorer import OrphanetDataManager

# Initialize processor
processor = OrphanetDataManager(output_dir="output")

# Define input files
xml_files = {
    "phenotype": "data/en_phenotype.xml",
    "consequences": "data/en_funct_consequences.xml",
    "natural_history": "data/en_nat_hist_ages.xml",
    "references": "data/references.xml",
    "epidemiology": "data/en_epidimiology_prev.xml"
}

# Process files and save merged dataset
merged_data = processor.process_files(
    xml_files,
    output_file="merged_orphanet_data.csv"
)
```

## Use Cases

1. **Medical Research**
   - Analyze disease phenotypes and their frequencies
   - Study disease inheritance patterns
   - Investigate prevalence across different populations

2. **Clinical Applications**
   - Build reference databases for rare diseases
   - Support diagnostic systems
   - Track epidemiological patterns

3. **Data Integration**
   - Combine Orphanet data with other medical databases
   - Create comprehensive disease profiles
   - Support machine learning models for disease classification


### Basic Usage

```python
# Process a single file type
processor = OrphanetDataManager()
root = processor.parse_xml("phenotype.xml")
phenotype_data = processor.extract_phenotype_data(root)

# Merge multiple datasets
merged_data = processor.merge_datasets([df1, df2, df3])
```

## Contributing

We welcome contributions! 

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Orphanet for providing the source data
- The rare disease research community

## Citation

If you use this package in your research, please cite:

```bibtex
@software{orphanet_processor,
  author = A. Tinakoua,
  title = {Orphanet Explorer: A Python Package for Processing Orphanet Data},
  year = {2025},
  url = {https://github.com/atinak/orphanet_explorer}
}
```
