from __future__ import annotations

import json
import logging
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.stats import norm

logger = logging.getLogger("YARRtist")


def load_data(input_data):
    with Path(input_data).open() as file:
        return json.load(file)


def get_chip_type_from_config(config):
    chiptype = ""
    try:
        chiptype = next(iter(config.keys()))
    except IndexError:
        logger.error("One of your chip configuration files is empty")

    if chiptype not in {"RD53B", "ITKPIXV2"}:
        logger.warning(
            "Chip name in configuration not one of expected chip names (RD53B or ITKPIXV2)"
        )
    return chiptype


def get_geomId_sn_from_config(config_data):
    chip_type = get_chip_type_from_config(config_data)
    config_parameter = config_data[chip_type].get("Parameter", []) if chip_type else {}
    chip_id = config_parameter.get("ChipId", 0)
    chip_name = config_parameter.get("Name", "")

    if chip_id == 12:
        return 1, chip_name
    if chip_id == 13:
        return 2, chip_name
    if chip_id == 14:
        return 3, chip_name
    if chip_id == 15:
        return 4, chip_name
    return chip_id, chip_name


def create_img_grid(images_buf, grid, text=None):
    spacing = 10
    bkg_color = (255, 255, 255)

    images = [Image.open(p) for p in images_buf]

    max_width = max(img.width for img in images)
    max_height = max(img.height for img in images)

    rows, cols = grid
    total_width = cols * max_width + (cols - 1) * spacing
    total_height = rows * max_height + (rows - 1) * spacing

    text_height = 0
    if text is not None:
        try:
            font = ImageFont.truetype("arial.ttf", 24)
        except OSError:
            font = ImageFont.load_default()
        bbox = font.getbbox(text)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        total_height += text_height + spacing

    combined_image = Image.new("RGB", (total_width, total_height), bkg_color)

    for idx, img in enumerate(images):
        row, col = divmod(idx, cols)
        x = col * (max_width + spacing)
        y = row * (max_height + spacing)
        combined_image.paste(img, (x, y))

    if text is not None:
        draw = ImageDraw.Draw(combined_image)
        text_x = (total_width - text_width) // 2
        text_y = total_height - text_height - 50 * spacing
        draw.text((text_x, text_y), text, fill="black", font=font)

    return combined_image


def get_configs_from_connectivity(conn_data):
    configs = []

    for c in conn_data.get("chips", []):
        configs.append(c.get("config"))

    return configs


def data_from_config(config_data):
    plot_data = []

    chip_type = get_chip_type_from_config(config_data)
    config_pixel = config_data[chip_type].get("PixelConfig", []) if chip_type else []

    if config_pixel:
        pixelDataMap = {
            k: [dic[k] for dic in config_pixel] for k in config_pixel[0] if k != "Col"
        }

        for key, data in pixelDataMap.items():
            plot_data.append(
                {
                    "Data": data,
                    "Entries": np.sum(np.array(data)),
                    "Name": key + "-Map",
                    "Overflow": 0.0,
                    "Type": "Histo2d",
                    "Underflow": 0.0,
                    "x": {
                        "AxisTitle": "Column",
                        "Bins": 400,
                        "High": 400.5,
                        "Low": 0.5,
                    },
                    "y": {"AxisTitle": "Row", "Bins": 384, "High": 384.5, "Low": 0.5},
                    "z": {"AxisTitle": key},
                }
            )

            if key == "TDAC":
                flat = np.array(data).flatten()
                bins = np.linspace(-15.5, 15.5, 32)
                hist, _edges = np.histogram(flat, bins=bins)
                plot_data.append(
                    {
                        "Data": hist,
                        "Entries": np.sum(flat),
                        "Name": "TADC-Dist",
                        "Overflow": 0.0,
                        "Type": "Histo1d",
                        "Underflow": 0.0,
                        "x": {
                            "AxisTitle": "TDAC",
                            "Bins": 31,
                            "High": 15.5,
                            "Low": -15.5,
                        },
                        "y": {"AxisTitle": "Number of Pixels"},
                        "z": {"AxisTitle": "z"},
                    }
                )

    return plot_data


def fit_Histo1d(freq, bins):
    centers = []
    for i in range(len(bins)):
        centers.append(0.5 * (bins[i] + bins[i - 1]))

    data = np.repeat(centers, freq)

    return norm.fit(data)
