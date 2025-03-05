from __future__ import annotations

import logging
from io import BytesIO
from pathlib import Path
from typing import List

import numpy as np
import typer
from PIL import Image

from yarrtist.cli.globals import CONTEXT_SETTINGS, OPTIONS, LogLevel
from yarrtist.plotter.core_functions import (
    plot_fe_config,
    plot_fe_histo,
    plot_module_histo,
)
from yarrtist.utils.utils import (
    create_img_grid,
    data_from_config,
    get_chip_type_from_config,
    get_configs_from_connectivity,
    get_geomId_sn_from_config,
    load_data,
)

log = logging.getLogger("YARRtist")

app = typer.Typer(context_settings=CONTEXT_SETTINGS)


################### summary of module from YARR scan directory ###################
def module_summary(connectivity_files, scan_dir, summary_title):
    ## list test files
    tests_names = []

    files_list = [
        f.name
        for f in Path(scan_dir).iterdir()
        if f.is_file()
        and "0x" in f.name
        and all(layer not in f.name for layer in ["L0", "L1", "L2", "R0"])
        and ".json" in f.name
    ]

    for f in files_list:
        try:
            ct = f.split("_", 1)
            tests_names.append(ct[1].split(".")[0])
        except IndexError:
            continue

    tests_names = list(set(tests_names))

    for i, connectivity in enumerate(connectivity_files):
        ##read each connectivity and get chips
        config_dir = Path(connectivity).parent
        connectivity_data = load_data(connectivity)
        module = get_configs_from_connectivity(connectivity_data)
        log.info(f"Plotting for module {i + 1}")
        ordered_chips = [""] * len(module)
        chip_types = [""] * len(module)
        module_type = "Triplet" if len(ordered_chips) == 3 else "Quad"
        log.debug(f"Module is a {module_type}")
        images = []

        ##get name of each found chip
        for chip in module:
            chip_data = load_data(f"{config_dir}/{chip}")
            geomId, name = get_geomId_sn_from_config(chip_data)
            ctype = get_chip_type_from_config(chip_data)
            ordered_chips[geomId - 1] = name
            chip_types[geomId - 1] = ctype
        log.debug(f"Ordered chips in module {ordered_chips}")

        ##format data for each test  for whole module
        for test in tests_names:
            plot = {}
            plot["data"] = {}

            log.info(f"Plotting {test}")
            not_found = 0

            for geomId, chip in enumerate(ordered_chips):
                file_name = f"{chip}_{test}.json"
                log.debug(f"Plotting for chip {geomId + 1}: {chip}")
                if file_name not in files_list:
                    log.debug(f"Chip {chip} not found, filling with 0s")
                    not_found += 1
                    if "InjVcalDiff_Map" in test:
                        plot["data"].update(
                            {
                                geomId: np.zeros((153600, 101))
                                if chip_types[geomId] == "ITKPIXV2"
                                else np.zeros((153600, 61))
                            }
                        )
                    elif "InjVcalDiff" in test:
                        plot["data"].update(
                            {
                                geomId: np.zeros((101, 49))
                                if chip_types[geomId] == "ITKPIXV2"
                                else np.zeros((61, 49))
                            }
                        )
                    else:
                        plot["data"].update({geomId: np.zeros((400, 384))})
                    continue

                data = load_data(f"{scan_dir}/{file_name}")
                plot["type"] = data.get("Type")
                plot["title"] = data.get("Name")

                if plot.get("type") == "Histo2d":
                    data_arr = np.array(data.get("Data"))
                    if None in data_arr:
                        data_arr[np.equal(data_arr, None)] = 0
                    plot["data"].update({geomId: data_arr})
                else:
                    plot["data"].update({geomId: data})

            if (not_found == 4 and module_type == "Quad") or (
                not_found == 3 and module_type == "Triplet"
            ):
                log.debug("Skipping whole test for this module")
                continue
            plotter = plot_module_histo(plot, data, module_type, "", ordered_chips)
            buf = BytesIO()
            plotter.savefig(buf, format="png")
            images.append(buf)
            buf.seek(0)
            plotter.close()

        summary = [Image.open(p).convert("RGB") for p in images]
        summary[0].save(
            f"{scan_dir}/{summary_title}_{i}.pdf",
            save_all=True,
            append_images=summary[1:],
        )
        log.info(f"Plot summary saved in {scan_dir}/{summary_title}_{i}.pdf")


################### summary of module, divided per chip, from YARR scan directory ###################
def module_summary_perchip(connectivity_files, scan_dir, summary_title):
    ## list test files
    tests_names = []

    files_list = [
        f.name
        for f in Path(scan_dir).iterdir()
        if f.is_file()
        and "0x" in f.name
        and all(layer not in f.name for layer in ["L0", "L1", "L2", "R0"])
        and ".json" in f.name
    ]

    for f in files_list:
        try:
            ct = f.split("_", 1)
            tests_names.append(ct[1].split(".")[0])
        except IndexError:
            continue

    tests_names = list(set(tests_names))

    for i, connectivity in enumerate(connectivity_files):
        ##read each connectivity and get chips
        config_dir = Path(connectivity).parent
        connectivity_data = load_data(connectivity)
        module = get_configs_from_connectivity(connectivity_data)

        log.info(f"Plotting for module {i + 1}")
        chips_names = [""] * len(module)
        all_imgs = []
        for chip in module:
            geomId, name = get_geomId_sn_from_config(load_data(f"{config_dir}/{chip}"))
            chips_names[geomId - 1] = name
        log.debug(f"Ordered chips in module: {chips_names}")
        grid = (2, 2) if len(chips_names) == 4 else (1, 3)
        if len(chips_names) == 4:
            chips_names = [
                chips_names[0],
                chips_names[3],
                chips_names[1],
                chips_names[3],
            ]

        for t in tests_names:
            log.info(f"Plotting {t}")
            images = []
            for c in chips_names:
                try:
                    log.debug(f"Plotting for chip {c}")
                    data = load_data(f"{scan_dir}/{c}_{t}.json")
                except Exception:
                    log.debug("Test not found for this chip, skipping")
                    continue
                plotter = plot_fe_histo(data, c)
                buf = BytesIO()
                plotter.savefig(buf, format="png")
                images.append(buf)
                buf.seek(0)
                plotter.close()

            if len(images) > 0:
                test_img = create_img_grid(images, grid)
                all_imgs.append(test_img)

        summary = [p.convert("RGB") for p in all_imgs]

        summary[0].save(
            f"{scan_dir}/{summary_title}_{i}.pdf",
            save_all=True,
            append_images=all_imgs[1:],
        )
        log.info(f"Plot summary saved in {scan_dir}/{summary_title}_{i}.pdf")


################### summary of module config from YARR scan directory ###################
def module_config_summary(connectivity_files, scan_dir, summary_title):
    ##list before and after config file
    files_list = [
        f.name
        for f in Path(scan_dir).iterdir()
        if (f.is_file() and ".before" in f.name) or ".after" in f.name
    ]

    for i, connectivity in enumerate(connectivity_files):
        ##read each connectivity and get chips
        config_dir = Path(connectivity).parent
        connectivity_data = load_data(connectivity)
        module = get_configs_from_connectivity(connectivity_data)

        log.info(f"Plotting for module {i + 1}")
        ordered_chips = [""] * len(module)
        module_type = "Triplet" if len(ordered_chips) == 3 else "Quad"
        for chip in module:
            geomId, name = get_geomId_sn_from_config(load_data(f"{config_dir}/{chip}"))
            ordered_chips[geomId - 1] = name

        all_data_before = []
        all_data_after = []
        all_imgs = []
        for _geomId, chip in enumerate(ordered_chips):
            ba_configs = [f for f in files_list if chip in f]
            if len(ba_configs) == 0:
                all_data_before.append([{}] * 5)
                all_data_after.append([{}] * 5)
                continue
            for conf in ba_configs:
                if ".before" in conf:
                    all_data_before.append(
                        data_from_config(load_data(f"{scan_dir}/{conf}"))
                    )
                elif ".after" in conf:
                    all_data_after.append(
                        data_from_config(load_data(f"{scan_dir}/{conf}"))
                    )

        all_data_before = list(map(list, zip(*all_data_before)))
        all_data_after = list(map(list, zip(*all_data_after)))

        for n in range(len(all_data_before)):
            plot_before = {}
            plot_after = {}
            plot_before["data"] = {}
            plot_after["data"] = {}
            images = []
            for geomId, (tb, ta) in enumerate(
                zip(all_data_before[n], all_data_after[n])
            ):
                if not tb or not ta:
                    plot_before["data"].update({geomId: np.zeros((400, 384))})
                    plot_after["data"].update({geomId: np.zeros((400, 384))})
                    continue
                plot_before["type"] = tb.get("Type")
                plot_after["type"] = ta.get("Type")
                plot_before["title"] = tb.get("Name") + " (before)"
                plot_after["title"] = ta.get("Name") + " (after)"
                if plot_before.get("type") == "Histo2d":
                    data_arr = np.array(tb.get("Data"))
                    plot_before["data"].update({geomId: data_arr})
                else:
                    plot_before["data"].update({geomId: tb})
                if plot_after.get("type") == "Histo2d":
                    data_arr = np.array(ta.get("Data"))
                    plot_after["data"].update({geomId: data_arr})
                else:
                    plot_after["data"].update({geomId: ta})
            plotter = plot_module_histo(plot_before, tb, module_type, "", ordered_chips)
            buf = BytesIO()
            plotter.savefig(buf, format="png")
            images.append(buf)
            buf.seek(0)
            plotter.close()
            plotter = plot_module_histo(plot_after, ta, module_type, "", ordered_chips)
            buf = BytesIO()
            plotter.savefig(buf, format="png")
            images.append(buf)
            buf.seek(0)
            plotter.close()
            all_imgs.append(create_img_grid(images, (1, 2)))

        summary = [p.convert("RGB") for p in all_imgs]

        summary[0].save(
            f"{scan_dir}/{summary_title}_{i}.pdf",
            save_all=True,
            append_images=all_imgs[1:],
        )
        log.info(f"Config summary saved in {scan_dir}/{summary_title}_{i}.pdf")


################### summary of module config, divided per chip, from YARR scan directory ###################
def module_config_summary_perchip(connectivity_files, scan_dir, summary_title):
    ##list all before and after files
    files_list = [
        f.name
        for f in Path(scan_dir).iterdir()
        if (f.is_file() and ".before" in f.name) or ".after" in f.name
    ]

    for i, connectivity in enumerate(connectivity_files):
        ##read each connectivity and get chips
        config_dir = Path(connectivity).parent
        connectivity_data = load_data(connectivity)
        module = get_configs_from_connectivity(connectivity_data)

        log.info(f"Plotting for module {i + 1}")
        chips_names = [""] * len(module)
        all_imgs = []
        for chip in module:
            geomId, name = get_geomId_sn_from_config(load_data(f"{config_dir}/{chip}"))
            chips_names[geomId - 1] = name

        for chip in chips_names:
            images = []
            configs = [f for f in files_list if ".before" in f and chip in f]
            if len(configs) == 0:
                continue
            config = configs[0]
            config_data = load_data(f"{scan_dir}/{config}")
            plotters = plot_fe_config(config_data)
            for k in plotters:
                buf = BytesIO()
                plotters[k].savefig(buf, format="png")
                images.append(buf)
                buf.seek(0)
            chip_img = create_img_grid(images, (2, 2), f"{chip} (before)")
            all_imgs.append(chip_img)

        for chip in chips_names:
            images = []
            configs = [f for f in files_list if ".after" in f and chip in f]
            if len(configs) == 0:
                continue
            config = configs[0]
            config_data = load_data(f"{scan_dir}/{config}")
            plotters = plot_fe_config(config_data)
            for k in plotters:
                buf = BytesIO()
                plotters[k].savefig(buf, format="png")
                images.append(buf)
                buf.seek(0)
            chip_img = create_img_grid(images, (2, 2), f"{chip} (after)")
            all_imgs.append(chip_img)

        summary = [p.convert("RGB") for p in all_imgs]
        summary[0].save(
            f"{scan_dir}/{summary_title}_{i}.pdf",
            save_all=True,
            append_images=all_imgs[1:],
        )
        log.info(f"Config summary saved in {scan_dir}/{summary_title}_{i}.pdf")


@app.command()
def main(
    connectivity_files: List[Path] = OPTIONS["connectivity_files"],
    scan_directory: Path = OPTIONS["scan_directory"],
    per_chip: bool = OPTIONS["per_chip"],
    config_summary: bool = OPTIONS["config_summary"],
    verbosity: LogLevel = OPTIONS["verbosity"],
):
    log.setLevel(verbosity.value)
    log.addHandler(logging.StreamHandler())

    if per_chip:
        log.info("Plotting module scan summary, divided per chip")
        module_summary_perchip(
            connectivity_files, scan_directory, "module_summary_perchip"
        )
        if config_summary:
            log.info("Plotting module config summary, divided per chip")
            module_config_summary_perchip(
                connectivity_files, scan_directory, "config_summary_perchip"
            )
    else:
        log.info("Plotting module scan summary")
        module_summary(connectivity_files, scan_directory, "module_summary")
        if config_summary:
            log.info("Plotting module config summary")
            module_config_summary(connectivity_files, scan_directory, "config_summary")
