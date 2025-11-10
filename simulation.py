import os
import shutil
import subprocess
import time

CASE_TEMPLATE_DIR = "CASE_TEMPLATE"

class SimulationManager:
    def __init__(self, template_dir=CASE_TEMPLATE_DIR):
        self.template_dir = template_dir

    def create_case_from_template(self, inputs, stl_paths):
        """
        Create a new case directory from template and update parameters.
        Supports multiple STL files.
        """
        run_id = time.strftime("%Y%m%d-%H%M%S")
        case_dir = os.path.join("cases", f"case_{run_id}")

        # Recreate case directory from template
        if os.path.exists(case_dir):
            shutil.rmtree(case_dir)
        shutil.copytree(self.template_dir, case_dir)

        # Create triSurface directory (for multiple geometries)
        tri_surface_dir = os.path.join(case_dir, "constant", "triSurface")
        os.makedirs(tri_surface_dir, exist_ok=True)

        # Handle STL input — list or single path
        if isinstance(stl_paths, (list, tuple)):
            for stl_path in stl_paths:
                if not isinstance(stl_path, (str, bytes, os.PathLike)):
                    raise TypeError(f"Invalid STL path type: {type(stl_path)}")
                shutil.copy(stl_path, tri_surface_dir)
        else:
            shutil.copy(stl_paths, tri_surface_dir)

        # Update controlDict
        self._update_control_dict(os.path.join(case_dir, "system", "controlDict"), inputs)

        # Update physicalProperties
        self._update_physical_properties(os.path.join(case_dir, "constant", "physicalProperties"), inputs)

        return case_dir

    def _update_control_dict(self, filepath, inputs):
        lines = []
        with open(filepath, "r") as f:
            for line in f:
                if line.strip().startswith("startTime"):
                    lines.append(f"startTime       {inputs['startTime']};\n")
                elif line.strip().startswith("endTime"):
                    lines.append(f"endTime         {inputs['endTime']};\n")
                elif line.strip().startswith("deltaT"):
                    lines.append(f"deltaT          {inputs['deltaT']};\n")
                else:
                    lines.append(line)
        with open(filepath, "w") as f:
            f.writelines(lines)

    def _update_physical_properties(self, filepath, inputs):
        lines = []
        with open(filepath, "r") as f:
            for line in f:
                if line.strip().startswith("mu "):
                    parts = line.split()
                    parts[-1] = f"{inputs['mu']};"
                    lines.append(" ".join(parts) + "\n")
                elif line.strip().startswith("Pr "):
                    parts = line.split()
                    parts[-1] = f"{inputs['Pr']};"
                    lines.append(" ".join(parts) + "\n")
                else:
                    lines.append(line)
        with open(filepath, "w") as f:
            f.writelines(lines)

    def run_simulation(self, case_dir):
        """
        Run the solver with OpenFOAM sourced, capture logs.
        """
        env = os.environ.copy()
        bashrc = "/apps/codes/OpenFoam-12/OpenFOAM-12/etc/bashrc"

        command = f"bash -c 'source {bashrc} && cd {case_dir} && foamRun'"

        process = subprocess.Popen(
            command, shell=True,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            universal_newlines=True, executable="/bin/bash"
        )

        logs = ""
        for line in process.stdout:
            logs += line
        process.wait()

        return logs
