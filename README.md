# vep-ai-validation-tools

**vep-ai-validation-tools** is a collection of utilities designed for validating outputs from the Variant Effect Predictor (VEP) and similar bioinformatics pipelines. The tools leverage AI and traditional methods to automate and enhance the validation process of genetic variant annotations and predictions. This repository is maintained by [Abstract Data](https://github.com/Abstract-Data).

## Features

- **Automated Validation Pipelines**: Scripts and utilities to validate VEP outputs and other annotation tools.
- **AI-powered Analysis**: Integrates AI models for advanced validation, anomaly detection, and error classification.
- **Flexible Input Handling**: Supports various file formats such as VCF, JSON, and tabular text for input and output.
- **Comparison Tools**: Side-by-side comparison utilities for VEP outputs, enabling rapid identification of discrepancies.
- **Customizable Validation Rules**: Easily extend or modify validation logic to suit project-specific requirements.
- **Comprehensive Logging and Reporting**: Detailed logs and summary reports to track validation results and issues.

## Directory Structure

```
src/
  ├── validators/           # Core validation logic and rule sets
  ├── ai/                   # AI/ML models and inference scripts
  ├── comparators/          # File and result comparison utilities
  ├── parsers/              # Input/output parsing utilities
  ├── report/               # Reporting and logging tools
  └── utils/                # Shared utilities and helpers
```

## Getting Started

### Prerequisites

- Python 3.8+
- (Recommended) [poetry](https://python-poetry.org/) or `pip` for dependencies

### Installation

Clone the repository and install requirements:

```bash
git clone https://github.com/Abstract-Data/vep-ai-validation-tools.git
cd vep-ai-validation-tools
pip install -r requirements.txt
```

### Usage

#### 1. Validate a VEP Output

```bash
python -m src.validators.validate_vep --input path/to/vep_output.vcf
```

#### 2. Run AI-based Validation

```bash
python -m src.ai.run_inference --input path/to/vep_output.vcf
```

#### 3. Compare Two Annotation Results

```bash
python -m src.comparators.compare_results --file1 old_output.vcf --file2 new_output.vcf
```

#### 4. Generate a Validation Report

```bash
python -m src.report.generate_report --input validation_results.json
```

### Customization

- **Validation Rules**: Edit or extend `src/validators/rules.py` to customize how outputs are validated.
- **AI Models**: Swap or update models in the `src/ai/models/` directory.

## Contributing

Pull requests and issues are welcome! Please open an issue before submitting major changes.

## License

This project is licensed under the MIT License.

## Contact

For questions or support, please contact [Abstract Data](https://github.com/Abstract-Data).
