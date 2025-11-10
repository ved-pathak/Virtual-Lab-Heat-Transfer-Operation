# Virtual Lab Heat Transfer Operations

A **Virtual Laboratory Framework** for simulating **laminar forced convection heat transfer** using **OpenFOAM** and **ParaView**, wrapped in an intuitive **Streamlit** web interface.
Developed as part of a virtual lab initiative to make CFD simulations accessible to students without prior command-line experience.

---

## 🚀 Overview

This project provides an interactive platform for students and researchers to:

* Simulate **3D or 2D/axisymmetric** developing flow in a pipe.
* Compare **constant wall temperature** vs **constant wall heat flux** conditions.
* Compute **local and average Nusselt numbers** for the developing region.
* Visualize results directly within a **Streamlit dashboard**.

The system automates the entire OpenFOAM workflow — from case setup to post-processing — allowing users to focus on physical insights rather than simulation commands.

---

## 🧰 Key Components

| File                 | Description                                                                                 |
| -------------------- | ------------------------------------------------------------------------------------------- |
| `app.py`             | Streamlit-based user interface for parameter input, simulation control, and result display. |
| `simulation.py`      | Core backend logic managing case creation, modification, and OpenFOAM solver execution.     |
| `post_process.py`    | Handles ParaView post-processing via `pvpython`, generating velocity and temperature plots. |
| `CASE_TEMPLATE/`     | Directory (to be created by the user) where base case templates are extracted.              |
| `case_templates.zip` | Predefined OpenFOAM case setups for different boundary conditions.                          |

---

## 🧩 Features

* **Web-based GUI:** Launch simulations with one click using Streamlit.
* **Automated case management:** Dynamically generates OpenFOAM cases from templates.
* **Solver integration:** Runs custom solvers with environment sourcing.
* **ParaView post-processing:** Automatically renders visual results and displays them in-app.
* **Extensible architecture:** Clean separation between interface, control, and simulation logic (MVC pattern).

---

## ⚙️ Installation Guide

### 1. Clone the Repository

```bash
git clone https://github.com/ved-pathak/Virtual-Lab-Heat-Transfer-Operation/
```

### 2. Create and Activate a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate   # On Windows use: venv\Scripts\activate
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install External Dependencies

You must have **OpenFOAM** and **ParaView** installed and accessible from your environment.

**Ubuntu (recommended):**

```bash
sudo apt install openfoam paraview
```

Make sure `foamRun` or your chosen solver is available in your `$PATH`.

---

## 🧾 Setup Instructions

1. **Update the solver path**
   In `simulation.py`, modify the solver command path if needed:

   ```python
   solver_command = "/opt/openfoam10/bin/foamRun"  # Update this as per your setup
   ```

2. **Unzip Case Templates**

   ```bash
   unzip case_templates.zip
   ```

3. **Create an Empty CASE_TEMPLATE Directory**

   ```bash
   mkdir CASE_TEMPLATE
   ```

4. **Move the Extracted Templates**
   Place the extracted case template folders into the `CASE_TEMPLATE` directory.

---

## ▶️ Running the Application

After setup, start the virtual lab dashboard with:

```bash
streamlit run app.py
```

Then open the displayed local URL in your browser (e.g., `http://localhost:8501`).

---

## 🧠 User Workflow

1. **Select Case Type:** Choose between constant temperature or constant flux boundary conditions.
2. **Upload Geometry:** Provide `.stl` files for the simulation domain.
3. **Input Parameters:** Define viscosity, Prandtl number, simulation duration, etc.
4. **Run Simulation:** The app automatically:

   * Creates an OpenFOAM case from the template
   * Executes the solver
   * Performs ParaView post-processing
5. **View Results:** Generated plots and solver logs appear on the dashboard.

---

## 📈 Future Enhancements

* In-browser geometry generation.
* Support for conjugate heat transfer and double-pipe heat exchangers.
* Advanced visualization (Nu vs x plots, animations).
* User authentication for multi-user deployment.

---

## 👨‍💻 Author

**Ved Pathak**
Department of Chemical Engineering
**Indian Institute of Technology Indore**
📅 *November 2025*

---

## 🧾 License

This project is released under the **MIT License**.
Feel free to use, modify, and distribute with attribution.
