import os
import logging
from ewokscore import Task
from .utils import create_run_file

logger = logging.getLogger(__name__)


class createRunFiles(
    Task,
    input_names=["output", "run_parameters"],
    output_names=["saved_files_path"],
):
    def run(self):
        args = self.inputs
        saved_files = []
        scans = get_scans_from_user_parameters(args.run_parameters)
        # Compute the destination basename using the provided logic.
        destination_basename = (
            os.path.basename(args.output)
            .replace("_{index}", "")
            .replace(".esperanto", "")
        )
        destination_dir = os.path.dirname(args.output)
        destination = os.path.join(destination_dir, destination_basename)

        logger.info(
            f"Starting createRunFiles task for file: {destination_basename}.run"
        )
        logger.debug(f"Computed destination: {destination}")

        create_run_file(
            scans, destination_dir, destination_basename
        )  # This doesn't take the .run ext
        saved_files.append(destination + ".run")
        logger.info(f"Created {destination}.run")

        self.outputs.saved_files_path = saved_files
        logger.info(
            "createRunFiles task completed. Saved files: " + ", ".join(saved_files)
        )


def get_scans_from_user_parameters(run_parameters):
    return [
        [
            {
                "count": run_parameters.get("number_of_frames"),
                "omega": run_parameters.get("omega", 0),
                "omega_start": run_parameters.get("omega_start"),
                "omega_end": run_parameters.get("omega_end"),
                "pixel_size": run_parameters.get("pixel_size", 0.075),
                "omega_runs": None,
                "theta": run_parameters.get("theta"),
                "kappa": run_parameters.get("kappa"),
                "phi": run_parameters.get("phi"),
                "domega": run_parameters.get("domega", 0),
                "dtheta": run_parameters.get("dtheta", 0),
                "dkappa": run_parameters.get("dkappa", 0),
                "dphi": run_parameters.get("dphi", 0),
                "center_x": run_parameters.get("beam")[0],
                "center_y": run_parameters.get("beam")[1],
                "alpha": run_parameters.get("alpha"),
                "dist": run_parameters.get("distance"),
                "l1": run_parameters.get("wavelength"),
                "l2": run_parameters.get("wavelength"),
                "l12": run_parameters.get("wavelength"),
                "b": run_parameters.get("wavelength"),
                "mono": run_parameters.get("mono", 0.99),
                "monotype": "SYNCHROTRON",
                "chip": [1024, 1024],
                "Exposure_time": run_parameters.get("exposure_time"),
            }
        ]
    ]
