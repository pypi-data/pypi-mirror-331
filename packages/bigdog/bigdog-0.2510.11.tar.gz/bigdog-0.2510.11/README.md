# BigDog

## Introduction

This is a Python package currently under testing, temporarily named "bigdog". It includes ValueU and QuantityU, which are designed to handle numerical values with asymmetric uncertainty and physical units. This package provides a robust framework for managing uncertainties in scientific computations, extending traditional numerical representations with error propagation and unit management.

### Dependencies

- Python 3.6+
- `numpy`
- `scipy`
- `astropy`

### Key Features

- **ValueU**: Handles numerical values with asymmetric uncertainties.
- **QuantityU**: Extends `ValueU` by incorporating unit management using `Astropy`.
- Supports arithmetic operations with proper uncertainty propagation.
- Provides various comparison and formatting methods.
- Includes built-in documentation accessible via `.help()`.

## Installation

Currently, the package is in the alpha stage and requires manual installation. The package name "bigdog" is a temporary designation, and the latest version is **0.2510.10**.

### Installing the Package

To install the package, run the following command in your terminal:

```sh
pip install bigdog
```

### Importing and Using the Package

Once installed, you can import the necessary modules in your Python script or interactive console:

```python
from bigdog import ValueU, QuantityU
```

## Usage

### Accessing Documentation

To view detailed usage instructions for `ValueU` and `QuantityU`, use the built-in help function:

```python
ValueU().help()  # Displays detailed information on ValueU
QuantityU().help()  # Displays detailed information on QuantityU
```

These commands provide comprehensive details about object creation, mathematical operations, unit conversions, comparisons, and additional functionalities.

## License & Disclaimer

- Unauthorized modification and redistribution of the source code are strictly prohibited.
- The authors bear no responsibility for any errors, malfunctions, or unintended consequences resulting from code modifications.
- This package assumes all variables are independent (zero covariance). Users should exercise caution when working with correlated data.

## Credits

**Main Developer**: DH.Koh ([donghyeok.koh.code@gmail.com](mailto\:donghyeok.koh.code@gmail.com))\
**Collaborating Developers**: JH.Kim, KM.Heo\
**Alpha Testers**: None

## Changelog

### v0.2510.10 (2025-03-04)

- Fixed operation method priority bug.
- Improved help message formatting.
- Minor path-related fixes.

## Contact & Contributions

Bug reports and contributions are welcome! Please contact the main developer for more information.

