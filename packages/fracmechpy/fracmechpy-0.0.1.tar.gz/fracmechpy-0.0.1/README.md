# fracmechpy: Fracture Mechanics

## Overview
fracmechpy is a Python package that calculates the fatigue crack growth rate (da/dN) and the stress intensity factor range (ΔK) for Compact Tension (CT) specimens with the Secant method based on ASTM E647.

## Features
- Computes fatigue crack growth rate (da/dN)
- Computes stress intensity factor range (ΔK)
)
- Implements ASTM E647 standard
- Includes error handling for ASTM E647 validity limits

## Installation
### Installing from PyPI (Future Deployment)
If FracGrowM is available on PyPI, you can install it using:
```bash
pip install fracmechpy
```

### Installing from Source
To install the package manually:
1. Clone the repository:
   ```bash
   git clone https://github.com/dhaselib/fracmechpy.git
   ```
2. Navigate to the directory:
   ```bash
   cd FracGrowM
   ```
3. Install using pip:
   ```bash
   pip install .
   ```

Ensure you have NumPy installed using:
```bash
pip install numpy
```

## Function
### `Secant(N, af, ab, W, p_max, p_min, B)`
This function calculates the fatigue crack growth rate (da/dN) and the stress intensity factor range (ΔK) for a CT specimen.

#### Parameters:
- `N` (numpy array): Number of cycles
- `af` (numpy array): Crack length at the front face of the specimen
- `ab` (numpy array): Crack length at the back face of the specimen
- `W` (float): Width of the specimen
- `p_max` (float): Maximum applied load
- `p_min` (float): Minimum applied load
- `B` (float): Thickness of the specimen

#### Returns:
- `dadN` (numpy array): Fatigue crack growth rate (da/dN)
- `dK` (numpy array): Stress intensity factor range (ΔK)

## Example Usage
```python
# Sample input data
import numpy as np
from fracmechpy import Secant

# Sample input data
N = np.array([560000, 570000, 580000, 590000])
af = np.array([4.68, 5.04, 5.46, 5.86])
ab = np.array([4.52, 5.02, 5.35, 5.21])
W = 50  # Width in (mm)
p_max = 4000  # Maximum load in (N)
p_min = 400  # Minimum load in (N)
B = 5  # Thickness in (mm)

# Compute crack growth rate and stress intensity factor range
dadN, dK = Secant(N, af, ab, W, p_max, p_min, B)
print("da/dN:", dadN)
print("dK:", dK)
```

## Error Handling
The function enforces ASTM E647 validity limits for crack growth increments (da). If the increment exceeds the standard-defined limits based on α = aᵥₑ/W , the function prints an error message and returns `None`.

## License
This package is distributed under the MIT License.

## Contact
For questions or contributions, please reach out to the author dhaselib@gmail.com.

"# fracmechpy" 
