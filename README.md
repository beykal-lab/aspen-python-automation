# Aspen Plus Automation with Python

<a href="https://doi.org/10.5281/zenodo.19156362"><img src="https://zenodo.org/badge/984323471.svg" alt="DOI"></a>


This repository demonstrates how to automate **Aspen Plus** simulations using **Python**. The goal is to enable high-throughput simulation workflows for:

- ⚙️ Generating large datasets for **machine learning models**
- ⚙️ Performing **data-driven optimization**

Aspen's COM interface is used to programmatically set inputs, run simulations, and extract results — enabling thousands of simulations without manual interaction.

---

## Current Maintained Entry Points

The repository now separates the maintained chemical-design competition checks
from the original Aspen COM examples:

```powershell
python main.py --help
python main.py validate-week1 --root .
python scripts/validate_week1_pack.py --root .
python -m pytest
```

The original Aspen automation snippets are still available, but they should be
run explicitly through the legacy entry point so importing the project or asking
for help does not start Aspen:

```powershell
python main.py legacy-aspen-sample --script "Aspen_to_Data-driven optimization.py"
```

See `docs/codebase_assessment.md` for the current codebase evaluation and Git
management policy.

---

## 📁 Repository Structure
aspen-python-automation
- `main.py` : Use this file to Perform Latin Hypercube Sampling (LHS) to create a dataset for your machine learning models
- `Aspen_to_Data-driven optimization.py` :  Run Aspen Plus from optimizer input and return the output
  
**Other files needed to run the code:**

- Simulation.bkp   ====>> Aspen Plus file for main.py
- Desalination.bkp ====>> Aspen Plus backup file for optimization

---

## 🔧 Requirements
- Windows OS
- Aspen Plus installed (with COM interface enabled)
- Python 3.x

### 🐍 Python Libraries

Install required packages using:

```bash
pip install pywin32 smt numpy 
```
---
## 📌 Script 1: High-Throughput Simulations: `main.py`

**Purpose:** Automatically run Aspen Plus simulations using LHS across input variables. Users can implement their own preferred sampling approch as well, however, this requires the users to change sample design function `LHS()` to the desired one.

### 🔄 Workflow:
1. Define bounds for two Aspen Plus stream variables (e.g., total molar flow of streams S1 and S2).
2. Generate 10000 (or any values) input samples using LHS.
3. For each sample: Modify Aspen Plus input variables
4. Run Aspen Plus simulation
5. Extract results from the desired stream 
6. Export results to a CSV file (sample.csv)

   
## 📌 Script 2: Aspen Plus Optimization Interface: `Aspen_to_Data-driven optimization.py`

**Purpose:** Run a single Aspen Plus simulation using a decision variable from an external optimizer and return the calculated objective function value.
### 🔄 Workflow
1. Read decision variable (e.g., feed temperature) value from input.txt
2. Modify Aspen Plus block input
3. Run the simulation
4. Extract mass fractions, mass flows, and energy consumption (QNET)
5. Compute total energy usage
6. Export results to output.txt (used by external optimizer)

---
## 💡 Applications
- Surrogate modeling using regression, neural networks, etc.
- Black-box optimization (e.g., SciPy, DEAP, Bayesian methods)
- Process design exploration
- Uncertainty quantification

---
## 📌 Citation & Example Use Cases
To cite this automation code and explore its use cases, please cite and check these papers below:
- Surrogate Modeling: Building a machine learning model for chemical processes:
  > Shahbazi, A., Nikkhah, H., Aghayev, Z., and Beykal, B., 2024. Data-Driven Bi-Level Optimization of Hyperparameters for Machine Learning Models. In Proceedings of 2024 AIChE Annual Meeting. ISBN: 978-0-8169-1122-6.

- Energy Minimization: Reducing total energy consumption in a multi-effect evaporation unit:

  > Barochia, D., Nikkhah, N., and Beykal, B., 2024. Design and Optimization of a Multipurpose Zero Liquid Discharge Desalination Plant. Systems & Control Transactions, 3, 705-710. DOI: [10.69997/sct.142929](https://doi.org/10.69997/sct.142929).

- Sensitivity Analysis: Studying key operational parameter influence using data-driven modeling:
  > Nikkhah, A., Nikkhah, H., Shahbazi, A., Zarin, M.K.Z., Iz, D.B., Ebadi, M.T., Fakhroleslam, M. and Beykal, B., 2024. Cumin and eucalyptus essential oil standardization using fractional distillation: Data-driven optimization and techno-economic analysis. Food and Bioproducts Processing, 143, 90-101. DOI: [10.1016/j.fbp.2023.10.005](https://doi.org/10.1016/j.fbp.2023.10.005).

### For bibtex users

```bibtex
@article{nikkhah2024cumin,
  title={Cumin and eucalyptus essential oil standardization using fractional distillation: Data-driven optimization and techno-economic analysis},
  author={Nikkhah, Ali and Nikkhah, Hasan and Shahbazi, Amir and Zarin, Mona Kamelan Zargar and Iz, Duygu Beykal and Ebadi, Mohammad-Taghi and Fakhroleslam, Mohammad and Beykal, Burcu},
  journal={Food and Bioproducts Processing},
  volume={143},
  pages={90--101},
  year={2024},
  publisher={Elsevier}
}

@article{barochia2024design,
  title={Design and Optimization of a Multipurpose Zero Liquid Discharge Desalination Plant},
  author={Barochia, D and Nikkhah, H and Beykal, B},
  journal={Syst. Control. Trans.},
  volume={3},
  pages={705--710},
  year={2024}
}

@inproceedings{shahbazi2024data,
  title={Data-Driven Bi-Level Optimization of Hyperparameters for Machine Learning Models},
  author={Shahbazi, Amir and Nikkhah, Hasan and Aghayev, Zahir and Beykal, Burcu},
  booktitle={2024 AIChE Annual Meeting},
  year={2024},
  organization={AIChE}
}
