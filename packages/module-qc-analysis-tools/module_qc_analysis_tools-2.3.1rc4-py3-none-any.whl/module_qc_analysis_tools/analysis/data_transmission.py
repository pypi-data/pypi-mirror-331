from __future__ import annotations

import logging
from functools import partial

import arrow
import matplotlib.pyplot as plt
import numpy as np
from module_qc_data_tools import (
    get_layer_from_sn,
    get_nlanes_from_sn,
    outputDataFrame,
    qcDataFrame,
)

from module_qc_analysis_tools import __version__
from module_qc_analysis_tools.utils.analysis import (
    check_layer,
    perform_qc_analysis,
)
from module_qc_analysis_tools.utils.misc import (
    DataExtractor,
    JsonChecker,
    bcolors,
    get_qc_config,
)

TEST_TYPE = "DATA_TRANSMISSION"

log = logging.getLogger(TEST_TYPE)


def analyze(
    input_json,
    site="",
    input_layer="Unknown",
    qc_criteria_path=None,
):
    func = partial(
        analyze_chip,
        site=site,
        input_layer=input_layer,
        qc_criteria_path=qc_criteria_path,
    )

    results = []
    for chip in input_json:
        if isinstance(chip, list):
            for item in chip:
                result = func(item)
                if result:
                    results.append(result)
        else:
            result = func(chip)
            if result:
                results.append(result)

    return zip(*results)


def analyze_chip(
    input_json,
    site="",
    input_layer="Unknown",
    qc_criteria_path=None,
):
    inputDF = outputDataFrame(_dict=input_json)

    linestyles = ["solid", "dotted", "dashed", "dashdot"]
    markerstyles = ["*", "o", "v", "s"]
    colours = ["C0", "C1", "C2", "C3"]

    # Check file integrity
    checker = JsonChecker(inputDF, TEST_TYPE)

    try:
        checker.check()
    except BaseException as exc:
        log.exception(exc)
        log.error(
            bcolors.ERROR
            + " JsonChecker check not passed, skipping this input."
            + bcolors.ENDC
        )
        return None

    log.debug(" JsonChecker check passed!")

    #   Get info
    qcframe = inputDF.get_results()
    metadata = qcframe.get_meta_data()
    module_sn = metadata.get("ModuleSN")
    n_lanes_per_chip = get_nlanes_from_sn(module_sn)
    qc_config = get_qc_config(qc_criteria_path, TEST_TYPE, module_sn)

    if input_layer == "Unknown":
        try:
            layer = get_layer_from_sn(module_sn)
        except Exception:
            log.error(bcolors.WARNING + " Something went wrong." + bcolors.ENDC)
    else:
        log.warning(
            bcolors.WARNING
            + f" Overwriting default layer config {get_layer_from_sn(module_sn)} with manual input {input_layer}!"
            + bcolors.ENDC
        )
        layer = input_layer
    check_layer(layer)

    try:
        chipname = metadata.get("Name")
        log.debug(f" Found chip name = {chipname} from chip config")
    except Exception:
        log.error(
            bcolors.ERROR
            + f" Chip name not found in input from {input_json}, skipping."
            + bcolors.ENDC
        )
        return None

    institution = metadata.get("Institution")
    if site != "" and institution != "":
        log.warning(
            bcolors.WARNING
            + f" Overwriting default institution {institution} with manual input {site}!"
            + bcolors.ENDC
        )
        institution = site
    elif site != "":
        institution = site

    if institution == "":
        log.error(
            bcolors.ERROR
            + "No institution found. Please specify your testing site either in the measurement data or specify with the --site option. "
            + bcolors.ENDC
        )
        return None

    #   Calculate quanties
    extractor = DataExtractor(inputDF, TEST_TYPE)
    calculated_data = extractor.calculate()

    log.debug(calculated_data)

    passes_qc = True
    summary = np.empty((0, 4), str)

    DELAY = calculated_data["Delay"]["Values"]
    EYE_OPENING = []
    EYE_WIDTH = []
    DELAY_SETTING = []

    fig, ax = plt.subplots()

    for lane in range(len(calculated_data.keys()) - 1):
        EYE_OPENING.append(calculated_data[f"EyeOpening{lane}"]["Values"])

        start_val = 0
        width = 0
        last_width = 0
        best_val = 0
        best_width = 0
        best_delay = 0

        for j in DELAY:
            if EYE_OPENING[-1][j] == 1:
                if width == 0:
                    start_val = j
                width += 1
                if j == DELAY[-1] and width > last_width:
                    best_val = start_val
                    best_width = width
            else:
                if width > last_width:
                    best_val = start_val
                    best_width = width
                last_width = best_width
                width = 0

        if best_width != 0:
            best_delay = int(best_val + (best_width / 2))
            log.info(
                f"Delay setting for lane {lane} with eye width {best_width}: {best_delay}"
            )
        else:
            log.info(f"No good delay setting for lane {lane}")

        EYE_WIDTH.append(best_width)
        DELAY_SETTING.append(best_delay)

        # # Internal eye diagram visualisation
        ax.step(
            calculated_data["Delay"]["Values"],
            calculated_data[f"EyeOpening{lane}"]["Values"],
            linestyle=linestyles[lane],
            color=colours[lane],
            label=f"Eye Opening [{lane}]: {best_width}",
        )
        ax.plot(
            best_delay,
            1,
            linestyle="None",
            marker=markerstyles[lane],
            markersize=5,
            color=colours[lane],
            label=f"Best Delay [{lane}]: {best_delay}",
        )

        ax.legend()

        # Load values to dictionary for QC analysis
        results = {}
        results.update({"EYE_WIDTH": best_width})

        # Perform QC analysis

        passes_qc, summary, _rounded_results = perform_qc_analysis(
            TEST_TYPE, qc_config, layer, results
        )

        ax.set_xlabel("Delay")
        ax.set_ylabel("Eye Opening")
        ax.set_title(f"{module_sn} {chipname}")
        plt.grid()
        plt.tight_layout()

    #  Output a json file
    outputDF = outputDataFrame()
    outputDF.set_test_type(TEST_TYPE)
    data = qcDataFrame()
    data._meta_data.update(metadata)
    data.add_property(
        "ANALYSIS_VERSION",
        __version__,
    )
    try:
        data.add_property(
            "YARR_VERSION",
            qcframe.get_properties().get("YARR_VERSION"),
        )
    except Exception as e:
        log.warning(f"Unable to find YARR version! Require YARR >= v1.5.2. {e}")
        data.add_property("YARR_VERSION", "")
    data.add_meta_data(
        "MEASUREMENT_VERSION",
        qcframe.get_properties().get(TEST_TYPE + "_MEASUREMENT_VERSION"),
    )
    time_start = qcframe.get_meta_data()["TimeStart"]
    time_end = qcframe.get_meta_data()["TimeEnd"]
    duration = arrow.get(time_end) - arrow.get(time_start)

    data.add_property(
        "MEASUREMENT_DATE",
        arrow.get(time_start).isoformat(timespec="milliseconds"),
    )
    data.add_property("MEASUREMENT_DURATION", int(duration.total_seconds()))

    data.add_meta_data("QC_LAYER", layer)
    data.add_meta_data("INSTITUTION", institution)

    # Add eye widths to output file
    for lane in range(n_lanes_per_chip):
        data.add_parameter(f"EYE_WIDTH{lane}", EYE_WIDTH[lane], 0)

    outputDF.set_results(data)
    outputDF.set_pass_flag(passes_qc)

    return chipname, outputDF.to_dict(True), passes_qc, summary, fig
