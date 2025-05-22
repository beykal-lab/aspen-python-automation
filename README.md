# Aspen Plus Automation with Python

This repository demonstrates how to automate **Aspen Plus** simulations using **Python**. The goal is to enable high-throughput simulation workflows for:

- ⚙️Generating large datasets for **machine learning models**
- ⚙️ Performing **data-driven optimization**

Aspen's COM interface is used to programmatically set inputs, run simulations, and extract results — enabling thousands of simulations without manual interaction.

---

## 📁 Repository Structure
aspen-python-automation
- main.py : Use this file to Perform LHS sampling to create dataset for your machine learning models
- Aspen_to_Data-driven optimization.py :  Run Aspen from optimizer input and return output
  
**Other files needed to run the code:**

- Simulation.bkp   ====>> Aspen  file for main.py
- Desalination.bkp ====>> Aspen backup file for optimization

README.md # You are here

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
---
📌 **Script 1: High-Throughput Simulations using LHS: main.py**


**Purpose:** Automatically run Aspen simulations using Latin Hypercube Sampling (LHS) across  input variables.
### 🔄 Workflow:
1. Define bounds for two Aspen stream variables (e.g., total molar flow of streams S1 and S2).
2. Generate 10000 (or any values) input samples using Latin Hypercube Sampling.
3. For each sample: Modify Aspen input variables
4. Run Aspen simulation
5. Extract results from the desired stream 
6. Save results to a CSV file (sample.csv)

   
📌 **Script 2: Aspen Optimization Interface:  Aspen_to_Data-driven optimization.py**

**Purpose:** Run a single Aspen simulation using a decision variable from an external optimizer and return the calculated objective function value.
### 🔄 Workflow
1. Read decision variable (e.g., feed temperature) from input.txt
2. Modify Aspen block input
3. Run the simulation
4. Extract mass fractions, mass flows, and energy consumption (QNET)
5. Compute total energy usage
6. Save result to output.txt (used by external optimizer)

---
## 💡 Applications
Surrogate modeling using regression, neural networks, etc.

Black-box optimization (SciPy, DEAP, Bayesian methods)

Process design exploration

Uncertainty quantification

---

📌 Example Use Cases
- Surrogate Modeling: Building a surrogate model for chemical process. Please refer to: "*Shahbazi, A.,et al. “Data-Driven Bi-Level Optimization of Hyperparameters for Machine Learning Models.” 2024 AIChE Annual Meeting, AIChE, 2024.*"

- Energy Minimization: Reducing total energy consumption in a multi-effect evaporation unit.  Please refer to: https://doi.org/10.69997/sct.142929

- Sensitivity Analysis: Studying key operational parameter influence using data-driven modeling.  Please refer to: https://doi.org/10.1016/j.fbp.2023.10.005

📜 License
Developed for research in Hybrid Modeling & Systems Engineering Laboratory, University of Connecticut. To cite it, please cite the below papers :
1. *Nikkhah, A., et al. “Cumin and Eucalyptus Essential Oil Standardization Using Fractional Distillation: Data-Driven Optimization and Techno-Economic Analysis.” Food and Bioproducts Processing, vol. 143, 2024, pp. 90–101.*
2. *Barochia, D., Nikkhah, H., and Beykal, B. “Design and Optimization of a Multipurpose Zero Liquid Discharge Desalination Plant.” Systems & Control Transactions, vol. 3, 2024, pp. 705–710.*
3. *Shahbazi, A., Nikkhah, H., et al. “Data-Driven Bi-Level Optimization of Hyperparameters for Machine Learning Models.” 2024 AIChE Annual Meeting, AIChE, 2024.*

   
****


### ✅  If you use latex, here is the bibltex::
<details>
<summary>📚 Click to expand BibTeX citations</summary>

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
