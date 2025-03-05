from __future__ import annotations

import logging
from io import BytesIO
from pathlib import Path

import numpy as np
import typer
from PIL import Image

from yarrtist.cli.globals import CONTEXT_SETTINGS, OPTIONS, LogLevel
from yarrtist.plotter.core_functions import (
    plot_fe_config,
    plot_module_histo,
)
from yarrtist.utils.utils import (
    create_img_grid,
    data_from_config,
    get_configs_from_connectivity,
    get_geomId_sn_from_config,
    load_data,
)

log = logging.getLogger("YARRtist")

app = typer.Typer(context_settings=CONTEXT_SETTINGS)


def config_summary_perchip(connectivity_file, summary_title):
    module = get_configs_from_connectivity(load_data(connectivity_file))
    absolute_path = Path(connectivity_file).parent

    ordered_chips = [{}] * len(module)

    all_imgs = []

    for chip in module:
        geomId, name = get_geomId_sn_from_config(
            load_data(str(absolute_path) + "/" + chip)
        )
        ordered_chips[geomId - 1] = {name: chip}

    for item in ordered_chips:
        for name, chip in item.items():
            config_data = load_data(str(absolute_path) + "/" + chip)
            plotters = plot_fe_config(config_data)
            images = []
            for k in plotters:
                buf = BytesIO()
                plotters[k].savefig(buf, format="png")
                images.append(buf)
                buf.seek(0)
            chip_img = create_img_grid(images, (2, 2), f"{name}")
            all_imgs.append(chip_img)

    summary = [p.convert("RGB") for p in all_imgs]
    summary[0].save(
        f"{absolute_path}/{summary_title}.pdf",
        save_all=True,
        append_images=all_imgs[1:],
    )
    log.info(f"Config summary saved in {absolute_path}/{summary_title}.pdf")


def config_summary(connectivity_file, summary_title):
    module = get_configs_from_connectivity(load_data(connectivity_file))
    absolute_path = Path(connectivity_file).parent

    ordered_chips = [""] * len(module)
    ordered_chips_names = [""] * len(module)

    all_imgs = []
    all_data = []

    for chip in module:
        geomId, name = get_geomId_sn_from_config(
            load_data(str(absolute_path) + "/" + chip)
        )
        ordered_chips[geomId - 1] = chip
        ordered_chips_names[geomId - 1] = name

    module_type = "Triplet" if len(ordered_chips) == 3 else "Quad"

    for chip in ordered_chips:
        all_data.append(data_from_config(load_data(str(absolute_path) + "/" + chip)))

    all_data = list(map(list, zip(*all_data)))
    plot = {}
    plot["data"] = {}

    for n in range(len(all_data)):
        for geomId, test in enumerate(all_data[n]):
            plot["type"] = test.get("Type")
            plot["title"] = test.get("Name")
            if plot.get("type") == "Histo2d":
                data_arr = np.array(test.get("Data"))
                plot["data"].update({geomId: data_arr})
            else:
                plot["data"].update({geomId: test})
        plotter = plot_module_histo(plot, test, module_type, "", ordered_chips_names)
        buf = BytesIO()
        plotter.savefig(buf, format="png")
        all_imgs.append(buf)
        buf.seek(0)
        plotter.close()

    summary = [Image.open(p).convert("RGB") for p in all_imgs]
    summary[0].save(
        f"{absolute_path}/{summary_title}.pdf", save_all=True, append_images=summary[1:]
    )
    log.info(f"Config summary saved in {absolute_path}/{summary_title}.pdf")


@app.command()
def main(
    input_file: Path = OPTIONS["input_file"],
    per_chip: bool = OPTIONS["per_chip"],
    verbosity: LogLevel = OPTIONS["verbosity"],
):
    log.setLevel(verbosity.value)
    log.addHandler(logging.StreamHandler())

    log.info(f"Plotting config summary from {input_file}")

    if per_chip:
        config_summary_perchip(input_file, "config_summary_perchip")
    else:
        config_summary(input_file, "config_summary")
