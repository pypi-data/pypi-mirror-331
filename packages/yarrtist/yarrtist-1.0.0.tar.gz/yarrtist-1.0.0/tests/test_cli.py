from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from yarrtist.cli import app


@pytest.fixture
def config_path():
    return Path() / "src" / "yarrtist" / "data" / "example_configs"


@pytest.fixture
def scan_path():
    return Path() / "src" / "yarrtist" / "data" / "example_scans"


@pytest.fixture
def runner():
    return CliRunner(mix_stderr=False)


def test_single_plot(runner, scan_path, caplog):
    result = runner.invoke(
        app,
        args=[
            "plots",
            "plot-single-test",
            "-i",
            scan_path.joinpath(
                "007134_std_thresholdscan_hd/0x17529_ThresholdDist-0.json"
            ),
            "-v",
            "DEBUG",
        ],
        catch_exceptions=False,
    )

    assert result.exit_code == 0
    assert "File saved in" in caplog.text


def test_single_config(runner, config_path, caplog):
    result = runner.invoke(
        app,
        args=[
            "plots",
            "plot-single-config",
            "-i",
            config_path.joinpath("20UPGM22200156/L2_warm/0x17529_L2_warm.json"),
            "-v",
            "DEBUG",
        ],
        catch_exceptions=False,
    )

    assert result.exit_code == 0
    assert "File saved in" in caplog.text


def test_scan(runner, config_path, scan_path, caplog):
    result = runner.invoke(
        app,
        args=[
            "plots",
            "plot-scan",
            "-c",
            config_path.joinpath("20UPGM22200156/20UPGM22200156_L2_warm.json"),
            "-s",
            scan_path.joinpath("007134_std_thresholdscan_hd"),
            "-v",
            "DEBUG",
        ],
        catch_exceptions=False,
    )

    assert result.exit_code == 0
    assert "Plot summary saved" in caplog.text
    assert "Config summary saved" in caplog.text


def test_scan_perchip(runner, config_path, scan_path, caplog):
    result = runner.invoke(
        app,
        args=[
            "plots",
            "plot-scan",
            "-c",
            config_path.joinpath("20UPGM22200156/20UPGM22200156_L2_warm.json"),
            "-s",
            scan_path.joinpath("007134_std_thresholdscan_hd"),
            "--per-chip",
            "-v",
            "DEBUG",
        ],
        catch_exceptions=False,
    )

    assert result.exit_code == 0
    assert "Plot summary saved" in caplog.text
    assert "Config summary saved" in caplog.text


def test_config(runner, config_path, caplog):
    result = runner.invoke(
        app,
        args=[
            "plots",
            "plot-connectivity",
            "-i",
            config_path.joinpath("20UPGM22200156/20UPGM22200156_L2_warm.json"),
            "-v",
            "DEBUG",
        ],
        catch_exceptions=False,
    )

    assert result.exit_code == 0
    assert "Config summary saved in" in caplog.text


def test_config_perchip(runner, config_path, caplog):
    result = runner.invoke(
        app,
        args=[
            "plots",
            "plot-connectivity",
            "-i",
            config_path.joinpath("20UPGM22200156/20UPGM22200156_L2_warm.json"),
            "--per-chip",
            "-v",
            "DEBUG",
        ],
        catch_exceptions=False,
    )

    assert result.exit_code == 0
    assert "Config summary saved in" in caplog.text


def test_broken(runner, config_path, scan_path, caplog):
    result = runner.invoke(
        app,
        args=[
            "plots",
            "plot-scan",
            "-c",
            config_path.joinpath("20UPGM23211207/20UPGM23211207_L2_warm.json"),
            "-s",
            scan_path.joinpath("008505_std_thresholdscan_hr"),
            "-v",
            "DEBUG",
        ],
        catch_exceptions=False,
    )

    assert result.exit_code == 0
    assert "Plot summary saved" in caplog.text
    assert "Config summary saved" in caplog.text


def test_broken_perchip(runner, config_path, scan_path, caplog):
    result = runner.invoke(
        app,
        args=[
            "plots",
            "plot-scan",
            "-c",
            config_path.joinpath("20UPGM23211207/20UPGM23211207_L2_warm.json"),
            "-s",
            scan_path.joinpath("008505_std_thresholdscan_hr"),
            "--per-chip",
            "-v",
            "DEBUG",
        ],
        catch_exceptions=False,
    )

    assert result.exit_code == 0
    assert "Plot summary saved" in caplog.text
    assert "Config summary saved" in caplog.text


def test_triplet_scan(runner, config_path, scan_path, caplog):
    result = runner.invoke(
        app,
        args=[
            "plots",
            "plot-scan",
            "-c",
            config_path.joinpath("20UPIM52002140/20UPIM52002140_R0.5_warm.json"),
            "-s",
            scan_path.joinpath("005124_std_thresholdscan_hd"),
            "-v",
            "DEBUG",
        ],
        catch_exceptions=False,
    )

    assert result.exit_code == 0
    assert "Plot summary saved" in caplog.text
    assert "Config summary saved" in caplog.text


def test_triplet_scan_perchip(runner, config_path, scan_path, caplog):
    result = runner.invoke(
        app,
        args=[
            "plots",
            "plot-scan",
            "-c",
            config_path.joinpath("20UPIM52002140/20UPIM52002140_R0.5_warm.json"),
            "-s",
            scan_path.joinpath("005124_std_thresholdscan_hd"),
            "--per-chip",
            "-v",
            "DEBUG",
        ],
        catch_exceptions=False,
    )

    assert result.exit_code == 0
    assert "Plot summary saved" in caplog.text
    assert "Config summary saved" in caplog.text


def test_triplet_config(runner, config_path, caplog):
    result = runner.invoke(
        app,
        args=[
            "plots",
            "plot-connectivity",
            "-i",
            config_path.joinpath("20UPIM52002140/20UPIM52002140_R0.5_warm.json"),
            "-v",
            "DEBUG",
        ],
        catch_exceptions=False,
    )

    assert result.exit_code == 0
    assert "Config summary saved in" in caplog.text


def test_triplet_config_perchip(runner, config_path, caplog):
    result = runner.invoke(
        app,
        args=[
            "plots",
            "plot-connectivity",
            "-i",
            config_path.joinpath("20UPIM52002140/20UPIM52002140_R0.5_warm.json"),
            "--per-chip",
            "-v",
            "DEBUG",
        ],
        catch_exceptions=False,
    )

    assert result.exit_code == 0
    assert "Config summary saved in" in caplog.text


def test_combined(runner, config_path, scan_path, caplog):
    result = runner.invoke(
        app,
        args=[
            "plots",
            "plot-scan",
            "-c",
            config_path.joinpath("20UPGM23211207/20UPGM23211207_L2_warm.json"),
            "-c",
            config_path.joinpath("20UPGM22200156/20UPGM22200156_L2_warm.json"),
            "-s",
            scan_path.joinpath("combined_std_thresholdscan"),
            "-v",
            "DEBUG",
        ],
        catch_exceptions=False,
    )

    assert result.exit_code == 0
    assert "Plot summary saved" in caplog.text
    assert "Config summary saved" in caplog.text


def test_combined_perchip(runner, config_path, scan_path, caplog):
    result = runner.invoke(
        app,
        args=[
            "plots",
            "plot-scan",
            "-c",
            config_path.joinpath("20UPGM23211207/20UPGM23211207_L2_warm.json"),
            "-c",
            config_path.joinpath("20UPGM22200156/20UPGM22200156_L2_warm.json"),
            "-s",
            scan_path.joinpath("combined_std_thresholdscan"),
            "--per-chip",
            "-v",
            "DEBUG",
        ],
        catch_exceptions=False,
    )

    assert result.exit_code == 0
    assert "Plot summary saved" in caplog.text
    assert "Config summary saved" in caplog.text
