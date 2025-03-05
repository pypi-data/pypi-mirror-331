#
# Copyright (c) Lightly AG and affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#
from __future__ import annotations

import logging
import os
import platform
import sys
from dataclasses import dataclass
from importlib import metadata
from importlib.metadata import PackageNotFoundError
from typing import Sequence

import torch
from torch.cuda import _CudaDeviceProperties

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DependencyInformation:
    library: str
    version: str | None


@dataclass(frozen=True)
class SystemInformation:
    platform: str
    python_version: str
    lightly_train_version: str
    dependencies: Sequence[DependencyInformation]
    optional_dependencies: Sequence[DependencyInformation]
    cpu_count: int | None
    gpus: Sequence[_CudaDeviceProperties]


def get_system_information() -> SystemInformation:
    version_info = sys.version_info
    return SystemInformation(
        python_version=".".join(
            str(v) for v in (version_info.major, version_info.minor, version_info.micro)
        ),
        lightly_train_version=metadata.version("lightly-train"),
        dependencies=[
            _get_dependency_information(library=library)
            for library in [
                "torch",
                "torchvision",
                "pytorch-lightning",
                "Pillow",
                "pillow-simd",
            ]
        ],
        optional_dependencies=[
            _get_dependency_information(library=library)
            for library in [
                "super-gradients",
                "tensorboard",
                "timm",
                "ultralytics",
                "wandb",
            ]
        ],
        platform=platform.platform(),
        cpu_count=os.cpu_count(),
        gpus=[
            torch.cuda.get_device_properties(device)
            for device in range(torch.cuda.device_count())
        ],
    )


def log_system_information(system_information: SystemInformation) -> None:
    # Log platform information, Python version, and LightlyTrain version.
    logger.debug(f"Platform: {system_information.platform}")
    logger.debug(f"Python: {system_information.python_version}")
    logger.debug(f"LightlyTrain: {system_information.lightly_train_version}")

    # Log dependencies.
    _log_dependency_versions(
        dependencies=system_information.dependencies,
        optional_dependencies=system_information.optional_dependencies,
    )

    # Log cpu and gpu information.
    logger.debug(f"CPUs: {system_information.cpu_count}")
    logger.debug(f"GPUs: {len(system_information.gpus)}")
    for gpu in system_information.gpus:
        logger.debug(f" - {gpu.name} {gpu.major}.{gpu.minor} ({gpu.total_memory})")

    # Log environment variables.
    logger.debug("Environment variables:")
    for var in ["CUDA_VISIBLE_DEVICES", "SLURM_JOB_ID"]:
        value = os.environ.get(var)
        if value is not None:
            logger.debug(f" - {var}: {value}")


def _log_dependency_versions(
    dependencies: Sequence[DependencyInformation],
    optional_dependencies: Sequence[DependencyInformation],
) -> None:
    logger.debug("Dependencies:")
    for dep in dependencies:
        display_version = dep.version if dep.version is not None else "x"
        logger.debug(f" - {dep.library:<20} {display_version:>12}")
    logger.debug("Optional dependencies:")
    for dep in optional_dependencies:
        display_version = dep.version if dep.version is not None else "x"
        logger.debug(f" - {dep.library:<20} {display_version:>12}")


def _get_dependency_information(library: str) -> DependencyInformation:
    try:
        return DependencyInformation(library=library, version=metadata.version(library))
    except PackageNotFoundError:
        return DependencyInformation(library=library, version=None)
