import os
import numpy as np
from paraview.simple import *

def post_process(case_dir, assets_dir, L_char, k_fluid):
    """
    Perform post-processing on an OpenFOAM case including:
    - Nusselt number calculation from `wallHeatTransferCoeff`
    - Slice rendering of velocity (U) and temperature (T) fields using ParaView
    
    Parameters:
    case_dir (str): Path to the OpenFOAM case directory
    assets_dir (str): Directory for saving output CSV and images
    L_char (float): Characteristic length for Nusselt number calculation
    k_fluid (float): Fluid thermal conductivity
    """
    
    # ====================== Nusselt Number Calculation ======================

    def parse_h_values(filepath):
        """Extract scalar heat transfer coefficient (h) values from an OpenFOAM file."""
        try:
            with open(filepath, 'r') as f:
                lines = f.readlines()
        except FileNotFoundError:
            return None
        data_started = False
        h_values = []
        for line in lines:
            if line.strip() == '(':
                data_started = True
                continue
            if line.strip() == ')':
                break
            if data_started:
                try:
                    h_values.append(float(line.strip()))
                except (ValueError, IndexError):
                    continue
        return h_values

    os.makedirs(assets_dir, exist_ok=True)
    output_file = os.path.join(assets_dir, "nusselt_numbers.csv")

    print(f"📊 Calculating Nusselt Numbers for case: {case_dir}")
    time_dirs = [d for d in os.listdir(case_dir)
                 if os.path.isdir(os.path.join(case_dir, d)) and d.replace('.', '', 1).isdigit()]
    time_dirs.sort(key=float)

    if not time_dirs:
        print("❌ Error: No time directories found in case directory.")
        return

    with open(output_file, 'w') as f:
        f.write("Time,Average_h,Nusselt\n")
        for t in time_dirs:
            h_filepath = os.path.join(case_dir, t, 'wallHeatTransferCoeff')
            if not os.path.exists(h_filepath):
                continue

            h_list = parse_h_values(h_filepath)
            if h_list:
                avg_h = np.mean(h_list)
                nusselt_number = (avg_h * L_char) / k_fluid
                f.write(f"{t},{avg_h},{nusselt_number}\n")
                print(f"Time: {t}, Avg. h: {avg_h:.4f}, Nu: {nusselt_number:.2f}")

    print(f"✅ Nusselt number data saved to {output_file}")

    # ====================== ParaView Slice Rendering =======================

    case_foam = os.path.join(case_dir, "case.foam")

    paraview.simple._DisableFirstRenderCameraReset()
    renderView = GetActiveViewOrCreate('RenderView')
    renderView.ViewSize = [1920, 1080]

    reader = OpenFOAMReader(FileName=case_foam)
    reader.MeshRegions = ['internalMesh']
    reader.CellArrays = ['U', 'T', 'p', 'p_rgh', 'rho']
    reader.UpdatePipeline()

    timesteps = reader.TimestepValues
    bounds = reader.GetDataInformation().GetBounds()
    xmid = 0.5 * (bounds[0] + bounds[1])
    ymid = 0.5 * (bounds[2] + bounds[3])
    zmid = 0.1 * (bounds[4] + bounds[5])

    print(f"🎨 Rendering slices for case: {case_dir}")

    for t in timesteps:
        print(f"⏳ Processing timestep {t} ...")
        reader.UpdatePipeline(time=t)

        # ---- U Slice ----
        sliceU = Slice(Input=reader)
        sliceU.SliceType = 'Plane'
        sliceU.SliceType.Origin = [xmid, ymid, zmid]
        sliceU.SliceType.Normal = [1, 0, 0]

        calcU = Calculator(Input=sliceU)
        calcU.ResultArrayName = "U_mag"
        calcU.Function = "mag(U)"

        dispU = Show(calcU, renderView)
        ColorBy(dispU, ('POINTS', 'U_mag'))
        dispU.RescaleTransferFunctionToDataRange(True)

        renderView.ResetCamera()
        renderView.Update()

        SaveScreenshot(os.path.join(assets_dir, f"U_slice_t_{int(t)}.png"), renderView)
        Delete(dispU)
        Delete(calcU)
        Delete(sliceU)

        # ---- T Slice ----
        sliceT = Slice(Input=reader)
        sliceT.SliceType = 'Plane'
        sliceT.SliceType.Origin = [xmid, ymid, zmid]
        sliceT.SliceType.Normal = [1, 0, 0]

        calcT = Calculator(Input=sliceT)
        calcT.ResultArrayName = "T_copy"
        calcT.Function = "T"

        dispT = Show(calcT, renderView)
        ColorBy(dispT, ('POINTS', 'T_copy'))
        dispT.RescaleTransferFunctionToDataRange(True)

        renderView.CameraPosition = [2, 0, 0]
        renderView.CameraFocalPoint = [xmid, ymid, zmid]
        renderView.CameraViewUp = [0, 2, 0]
        renderView.ResetCamera()

        renderView.Update()
        SaveScreenshot(os.path.join(assets_dir, f"T_slice_t_{int(t)}.png"), renderView)

        Delete(dispT)
        Delete(calcT)
        Delete(sliceT)

        print(f"✅ Saved images for timestep {t}")

    print(f"🎉 All post-processing complete! Results saved in: {assets_dir}")
if __name__ == "__main__":
    # Ensure correct number of arguments
    if len(sys.argv) != 5:
        print("Usage: pvpython post_process.py <case_dir> <assets_dir> <L_char> <k_fluid>")
        sys.exit(1)

    case_dir = sys.argv[1]
    assets_dir = sys.argv[2]
    L_char = float(sys.argv[3])
    k_fluid = float(sys.argv[4])

    post_process(case_dir, assets_dir, L_char, k_fluid)
