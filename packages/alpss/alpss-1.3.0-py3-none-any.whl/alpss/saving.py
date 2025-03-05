import os
import pandas as pd
import numpy as np
from IPython.display import display


# function for saving all the final outputs
def save(
    sdf_out, cen, vc_out, sa_out, iua_out, fua_out, start_time, end_time, fig, **inputs
):
    fname = os.path.join(inputs["out_files_dir"], os.path.basename(inputs["filepath"]))

    # save the plots
    fig.savefig(
        fname=fname + "--plots.png",
        dpi="figure",
        format="png",
        facecolor="w",
    )

    # save the function inputs used for this run
    inputs_df = pd.DataFrame.from_dict(inputs, orient="index", columns=["Input"])
    inputs_df.to_csv(fname + "--inputs" + ".csv", index=True, header=False)

    # save the noisy velocity trace
    velocity_data = np.stack((vc_out["time_f"], vc_out["velocity_f"]), axis=1)
    np.savetxt(fname + "--velocity" + ".csv", velocity_data, delimiter=",")

    # save the smoothed velocity trace
    velocity_data_smooth = np.stack(
        (vc_out["time_f"], vc_out["velocity_f_smooth"]), axis=1
    )
    np.savetxt(
        fname + "--velocity--smooth" + ".csv",
        velocity_data_smooth,
        delimiter=",",
    )

    # save the filtered voltage data
    voltage_data = np.stack(
        (
            sdf_out["time"],
            np.real(vc_out["voltage_filt"]),
            np.imag(vc_out["voltage_filt"]),
        ),
        axis=1,
    )
    np.savetxt(fname + "--voltage" + ".csv", voltage_data, delimiter=",")

    # save the noise fraction
    noise_data = np.stack((vc_out["time_f"], iua_out["inst_noise"]), axis=1)
    np.savetxt(fname + "--noisefrac" + ".csv", noise_data, delimiter=",")

    # save the velocity uncertainty
    vel_uncert_data = np.stack((vc_out["time_f"], iua_out["vel_uncert"]), axis=1)
    np.savetxt(
        fname + "--veluncert" + ".csv",
        vel_uncert_data,
        delimiter=",",
    )

    # save the final results
    # results_to_save = {
    #     "Name": [
    #         "Date",
    #         "Time",
    #         "File Name",
    #         "Run Time",
    #         "Velocity at Max Compression",
    #         "Time at Max Compression",
    #         "Velocity at Max Tension",
    #         "Time at Max Tension",
    #         "Velocity at Recompression",
    #         "Time at Recompression",
    #         "Carrier Frequency",
    #         "Spall Strength",
    #         "Spall Strength Uncertainty",
    #         "Strain Rate",
    #         "Strain Rate Uncertainty",
    #         "Peak Shock Stress",
    #         "Spect Time Res",
    #         "Spect Freq Res",
    #         "Spect Velocity Res",
    #         "Signal Start Time",
    #         "Smoothing Characteristic Time",
    #     ],
    #     "Value": [
    #         start_time.strftime("%b %d %Y"),
    #         start_time.strftime("%I:%M %p"),
    #         os.path.basename(inputs["filepath"]),
    #         (end_time - start_time),
    #         sa_out["v_max_comp"],
    #         sa_out["t_max_comp"],
    #         sa_out["v_max_ten"],
    #         sa_out["t_max_ten"],
    #         sa_out["v_rc"],
    #         sa_out["t_rc"],
    #         cen,
    #         sa_out["spall_strength_est"],
    #         fua_out["spall_uncert"],
    #         sa_out["strain_rate_est"],
    #         fua_out["strain_rate_uncert"],
    #         (0.5 * inputs["density"] * inputs["C0"] * sa_out["v_max_comp"]),
    #         sdf_out["t_res"],
    #         sdf_out["f_res"],
    #         0.5 * (inputs["lam"] * sdf_out["f_res"]),
    #         sdf_out["t_start_corrected"],
    #         iua_out["tau"],
    #     ],
    # }
    # results_df = pd.DataFrame(data=results_to_save)
    # results_df.to_csv(fname + "--results" + ".csv", index=False, header=False)

    # # display the final results table in nanoseconds to make it more readable
    # # the data in the saved file is still in seconds
    # results_df.loc[5, "Value"] /= 1e-9
    # results_df.loc[7, "Value"] /= 1e-9
    # results_df.loc[9, "Value"] /= 1e-9
    # results_df.loc[16, "Value"] /= 1e-9
    # results_df.loc[19, "Value"] /= 1e-9
    # results_df.loc[20, "Value"] /= 1e-9

    results_to_save = {
        "Date": start_time.strftime("%b %d %Y"),
        "Time": start_time.strftime("%I:%M %p"),
        "File Name": os.path.basename(inputs["filepath"]),
        "Run Time": (end_time - start_time),
        "Velocity at Max Compression": sa_out["v_max_comp"],
        "Time at Max Compression": sa_out["t_max_comp"],
        "Velocity at Max Tension": sa_out["v_max_ten"],
        "Time at Max Tension": sa_out["t_max_ten"],
        "Velocity at Recompression": sa_out["v_rc"],
        "Time at Recompression": sa_out["t_rc"],
        "Carrier Frequency": cen,
        "Spall Strength": sa_out["spall_strength_est"],
        "Spall Strength Uncertainty": fua_out["spall_uncert"],
        "Strain Rate": sa_out["strain_rate_est"],
        "Strain Rate Uncertainty": fua_out["strain_rate_uncert"],
        "Peak Shock Stress": (
            0.5 * inputs["density"] * inputs["C0"] * sa_out["v_max_comp"]
        ),
        "Spect Time Res": sdf_out["t_res"],
        "Spect Freq Res": sdf_out["f_res"],
        "Spect Velocity Res": 0.5 * (inputs["lam"] * sdf_out["f_res"]),
        "Signal Start Time": sdf_out["t_start_corrected"],
        "Smoothing Characteristic Time": iua_out["tau"],
    }

    # Convert the dictionary to a DataFrame
    results_df = pd.DataFrame([results_to_save])

    # Optional: Convert units to nanoseconds for certain fields
    results_df.loc[0, "Velocity at Max Compression"] /= 1e-9
    results_df.loc[0, "Velocity at Max Tension"] /= 1e-9
    results_df.loc[0, "Velocity at Recompression"] /= 1e-9
    results_df.loc[0, "Spect Time Res"] /= 1e-9
    results_df.loc[0, "Spect Velocity Res"] /= 1e-9
    results_df.loc[0, "Signal Start Time"] /= 1e-9

    display(results_df)
    return results_to_save
