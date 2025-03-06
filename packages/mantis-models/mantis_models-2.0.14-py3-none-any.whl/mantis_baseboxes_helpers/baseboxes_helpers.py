# -*- coding: utf-8 -*-
import glob
import os
import tempfile
from pathlib import Path
from typing import Any
from typing import Dict
from typing import List

from ruamel.yaml import YAML


def validate_yaml_basebox_file(basebox_yaml_file_path: Path) -> None:
    """
    Validate (from a system point of view) a yaml basebox file
    :param yaml_basebox_file_path: path of the file
    :return: None
    """
    if not basebox_yaml_file_path.exists():
        raise Exception(
            "The provided YAML configuration path does not exist: '{}'".format(
                basebox_yaml_file_path
            )
        )

    if not basebox_yaml_file_path.is_file():
        raise Exception(
            "The provided YAML configuration path is not a file: '{}'".format(
                basebox_yaml_file_path
            )
        )

    if not os.access(str(basebox_yaml_file_path), os.R_OK):
        raise Exception(
            "The provided YAML configuration file is not readable: '{}'".format(
                basebox_yaml_file_path
            )
        )


def read_yaml_basebox_file(basebox_yaml_file_path: Path) -> str:
    """
    Read a yaml file and return its content
    :param yaml_basebox_file_path: path of the yaml file
    :return: the content of the file
    """
    with open(str(basebox_yaml_file_path), "r") as file:
        yaml_content = file.read()
        return yaml_content


def validate_basebox_id(basebox_subpath: Path, basebox_yaml: Dict[str, Any]) -> bool:
    """
    Validate that the id of the basebox is correct, according to its path
    Only if the id is present in the yaml file
    :param basebox_subpath: subpath of the basebox (eg AMOSSYS/ubuntu/ubuntu21.04)
    :param content: content of the basebox.yaml file
    :return: True if the id is correct, False otherwise
    """
    validation: bool = True
    if "id" in basebox_yaml:
        basebox_id: str = basebox_yaml["id"]
        validation = basebox_id == str(basebox_subpath)
        if not validation:
            raise Exception(
                f"The provided id in the YAML description file of {basebox_subpath} is not correct"
            )
    return validation


def list_baseboxes_yaml_on_disk(baseboxes_path: Path) -> List[Dict[str, Any]]:
    # check that the directory exists
    if not baseboxes_path.is_dir():
        raise NotADirectoryError(
            f"The provided baseboxes path '{baseboxes_path}' does not exist or is not a folder"
        )

    baseboxes: List[Dict[str, Any]] = []
    invalid_baseboxes: List[str] = []

    # Check that each basebox has a a yaml description
    # Read the YAML file
    for basebox_path_str in glob.glob(
        f"{baseboxes_path}/**/basebox.yaml", recursive=True
    ):
        basebox_yaml_file_path = Path(basebox_path_str)

        # Remove the basebox folder and the basebox.yaml from the path to get the basebox_id
        basebox_subpath = basebox_yaml_file_path.relative_to(baseboxes_path).parent

        # Check that the file exists and we have the rights to read it
        try:
            validate_yaml_basebox_file(basebox_yaml_file_path)
        except Exception as e:
            invalid_baseboxes.append(str(e))
            continue

        # Load the contents of the file
        basebox_yaml_str = read_yaml_basebox_file(basebox_yaml_file_path)
        basebox_yaml = YAML().load(basebox_yaml_str)

        # If the id is present, verify it, otherwise add it
        if "id" not in basebox_yaml:
            basebox_yaml["id"] = str(basebox_subpath)
            with tempfile.NamedTemporaryFile() as tmp:
                YAML().dump(basebox_yaml, tmp)
                tmp_path = Path(tmp.name)
                basebox_yaml_str = read_yaml_basebox_file(tmp_path)

        # Check coherence between the basebox id and its subpath
        try:
            validate_basebox_id(basebox_subpath, basebox_yaml)
        except Exception as e:
            invalid_baseboxes.append(str(e))

        baseboxes.append(basebox_yaml)

    if invalid_baseboxes:
        raise Exception(", ".join(invalid_baseboxes))

    return baseboxes


def list_baseboxes_img_on_disk(baseboxes_path: Path) -> List[str]:
    # check that the directory exists
    if not baseboxes_path.is_dir():
        raise NotADirectoryError(
            f"The provided baseboxes path '{baseboxes_path}' does not exist or is not a folder"
        )

    baseboxes: List[str] = []

    # Check that each basebox has a .img file
    for basebox_path_str in glob.glob(
        f"{baseboxes_path}/**/basebox.img", recursive=True
    ):
        basebox_img_file_path = Path(basebox_path_str)

        # Remove the basebox folder and the basebox.img from the path to get the basebox_id
        basebox_id = str(basebox_img_file_path.relative_to(baseboxes_path).parent)
        baseboxes.append(basebox_id)

    return baseboxes


def retrieve_basebox_yaml_on_disk(
    baseboxes_path: Path, basebox_id: str
) -> Dict[str, Any]:
    """Retrieve the YAML file associated with a local IMG file, if it
    exist. Those YAML files may exist for custom IMG basebox files.

    """
    # check that the directory exists
    if not baseboxes_path.is_dir():
        raise NotADirectoryError(
            f"The provided baseboxes path '{baseboxes_path}' does not exist or is not a folder"
        )

    basebox_path_str = f"{baseboxes_path}/{basebox_id}/basebox.yaml"
    basebox_yaml_file_path = Path(basebox_path_str)

    # Remove the basebox folder and the basebox.yaml from the path to get the basebox_id
    basebox_subpath = basebox_yaml_file_path.relative_to(baseboxes_path).parent

    # Check that the file exists and we have the rights to read it
    validate_yaml_basebox_file(basebox_yaml_file_path)

    # Load the contents of the file
    basebox_yaml_str = read_yaml_basebox_file(basebox_yaml_file_path)
    basebox_yaml = YAML().load(basebox_yaml_str)

    # If the id is present, verify it, otherwise add it
    if "id" not in basebox_yaml:
        basebox_yaml["id"] = str(basebox_subpath)
        with tempfile.NamedTemporaryFile() as tmp:
            YAML().dump(basebox_yaml, tmp)
            tmp_path = Path(tmp.name)
            basebox_yaml_str = read_yaml_basebox_file(tmp_path)

    # Check coherence between the basebox id and its subpath
    validate_basebox_id(basebox_subpath, basebox_yaml)

    return basebox_yaml
