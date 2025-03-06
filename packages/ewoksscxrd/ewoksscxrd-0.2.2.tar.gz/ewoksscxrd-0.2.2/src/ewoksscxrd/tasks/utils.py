import io
import os
from cryio import crysalis


def create_run_file(scans, crysalis_dir, basename):
    """
    Create a Crysalis run file using the provided scans.
    """
    runHeader = crysalis.RunHeader(basename.encode(), crysalis_dir.encode(), 1)
    runname = os.path.join(crysalis_dir, basename)
    runFile = []
    # Expecting scans to be a list of lists; process the first set of scans.
    for omega_run in scans[0]:
        dscr = crysalis.RunDscr(0)
        dscr.axis = crysalis.SCAN_AXIS["OMEGA"]
        dscr.kappa = omega_run["kappa"]
        dscr.omegaphi = 0
        dscr.start = omega_run["omega_start"]
        dscr.end = omega_run["omega_end"]
        dscr.width = omega_run["domega"]
        dscr.todo = dscr.done = omega_run["count"]
        dscr.exposure = 1
        runFile.append(dscr)
    crysalis.saveRun(runname, runHeader, runFile)
    crysalis.saveCrysalisExpSettings(crysalis_dir)


def create_par_file(par_file, processed_data_dir, basename):
    """
    Create a new .par file using the contents of the original.
    Changes any "FILE CHIP" line so that the referenced file ends with '.ccd'.
    """
    new_par = os.path.join(processed_data_dir, basename)
    with io.open(new_par, "w", encoding="iso-8859-1") as new_file:
        with io.open(par_file, "r", encoding="iso-8859-1") as old_file:
            for line in old_file:
                if line.startswith("FILE CHIP"):
                    new_file.write(f"FILE CHIP {basename.replace('.par','.ccd')} \n")
                else:
                    new_file.write(line)
