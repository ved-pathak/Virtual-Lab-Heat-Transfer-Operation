"""
### FILE: app.py
Streamlit web app GUI for simulation input, multiple STL upload, and results display.
"""
import os
import shutil
import streamlit as st
import sys
from simulation import SimulationManager
import subprocess

L_char = "0.2"  # Characteristic length for Nusselt number calculation


def run_post_process(case, assets_dir, L_char, k_fluid):
    cmd = (
        f'xvfb-run -s "-screen 0 1024x768x24" '
        f'pvpython post_process.py {case} {assets_dir} {L_char} {k_fluid}'
    )

    print("Running:", cmd)

    result = subprocess.Popen(
        cmd,
        shell=True,  # Interpret quotes correctly
        stdout=sys.stdout,
        stderr=sys.stderr,
        text=True,
    )
    result.wait()


# --- Streamlit Page Setup ---
st.set_page_config(page_title="OpenFOAM Runner", layout="wide")
st.title("OpenFOAM Runner")
# --- Simulation Type Selection ---
st.subheader("Simulation Type")
case_type = st.radio(
    "Select simulation type:",
    ("CONSTANT_FLUX", "CONSTANT_TEMP"),
    horizontal=True,
)
st.markdown(f"### 🔗 [Open Geometry Generator] https://colab.research.google.com/drive/1yfMfTfGrnHBnOlQHOGj8Dthk8smohOH4?usp=sharing")
# Define paths for templates
TEMPLATE_DIRS = {
    "CONSTANT_FLUX": "./CONSTANT_FLUX_TEMPLATE",
    "CONSTANT_TEMP": "./CONSTANT_TEMP_TEMPLATE",
}
WORKING_TEMPLATE = "./CASE_TEMPLATE"

# Copy correct template
try:
    if os.path.exists(WORKING_TEMPLATE):
        shutil.rmtree(WORKING_TEMPLATE)
    shutil.copytree(TEMPLATE_DIRS[case_type], WORKING_TEMPLATE)
    st.success(f"Using template: {case_type}")
except Exception as e:
    st.error(f"Error setting up template: {e}")

# --- Sidebar Inputs ---
st.sidebar.header("Simulation Parameters")

params = {}
params["mu"] = st.sidebar.text_input("Viscosity (mu)", "1e-3")
params["Pr"] = st.sidebar.text_input("Prandtl number (Pr)", "0.71")
params["startTime"] = st.sidebar.text_input("Start time", "0")
params["endTime"] = st.sidebar.text_input("End time", "10")
params["deltaT"] = st.sidebar.text_input("Time step (deltaT)", "0.001")
k_fluid = st.sidebar.text_input("Fluid thermal conductivity (k)", "0.6")

# --- Multi-file STL upload ---
st.sidebar.subheader("Geometry (.stl)")
stl_files = st.sidebar.file_uploader(
    "Upload one or more STL files",
    type=["stl"],
    accept_multiple_files=True
)

# --- Initialize Simulation Manager ---
sim_manager = SimulationManager()

# --- Run Simulation ---
if st.sidebar.button("RUN SIMULATION"):
    if not stl_files:
        st.error("Please upload at least one .stl geometry file")
    else:
        with st.spinner("Setting up case and running simulation..."):
            # Create temporary folder for STL uploads
            stl_tmp_dir = "/tmp/stl_inputs"
            os.makedirs(stl_tmp_dir, exist_ok=True)

            uploaded_paths = []
            for file in stl_files:
                tmp_path = os.path.join(stl_tmp_dir, file.name)
                with open(tmp_path, "wb") as f:
                    f.write(file.read())
                uploaded_paths.append(tmp_path)

            try:
                # Create case using multiple STL files
                case_dir = sim_manager.create_case_from_template(params, uploaded_paths)
                st.success(f"Case created at {case_dir}")

                # Run solver
                logs = sim_manager.run_simulation(case_dir)

                st.text_area("Solver Logs", logs, height=400)

                # Post-process results
                assets_dir = os.path.join(case_dir, "assets")
                os.makedirs(assets_dir, exist_ok=True)
                run_post_process(case_dir, assets_dir, L_char, k_fluid)
                st.success("Post-processing complete. Results ready.")
                # 💾 Show link to assets directory
                st.markdown(f"### 🔗 [Open Assets Folder]({os.path.abspath(assets_dir)})")

                # Display up to 4 images
                st.subheader("Results")
                imgs = [
                    os.path.join(assets_dir, f)
                    for f in os.listdir(assets_dir)
                    if f.lower().endswith((".png", ".jpg", ".jpeg", ".gif"))
                ]
                cols = st.columns(2)
                for i in range(4):
                    if i < len(imgs):
                        cols[i % 2].image(imgs[i], caption=os.path.basename(imgs[i]))
                    else:
                        cols[i % 2].info("(not generated)")

            except Exception as e:
                st.error(f"Error: {e}")
