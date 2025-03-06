#!/usr/bin/env python3
import json
import re
import shlex
import sys
import warnings
from argparse import ArgumentParser
from datetime import datetime
from pathlib import Path
from pprint import pprint
from subprocess import PIPE, run
from typing import Dict, List, Optional, Set, Tuple


class RefusalToBuildException(Exception):
    pass


ERROR_COLOR = "\033[01;31m"
NO_COLOR = "\033[00m"

VERSION_NUMBER_PATTERN = re.compile(r"v(\d[\d\.]+.*)")

# Would like to include timezone offset, but not worth the
# complexity of including pytz/etc.
TIMESTAMP_FORMAT = "%Y%m%d-%H%M%S%z"

# TODO: expand to other formats (JSON, YAML, CSV) in the future if necessary or appropriate
IMAGE_LIST_FILENAME = "docker_images.txt"

BASE_DIR_BUILD_OPTION = "base_directory_build"
GIT_VERSION_FILE_OPTION = "write_git_version"
GIT_JSON_FILE_OPTION = "write_git_json"
PLATFORMS_OPTION = "platforms"

SUPPORTED_OPTIONS = frozenset(
    {
        BASE_DIR_BUILD_OPTION,
        GIT_VERSION_FILE_OPTION,
        GIT_JSON_FILE_OPTION,
        PLATFORMS_OPTION,
    }
)

DOCKER = "docker"
DOCKER_BUILD_COMMAND_TEMPLATE: List[str] = [
    DOCKER,
    "build",
    "-q",
    "-t",
    "{label}",
    "-f",
    "{dockerfile_path}",
    ".",
]
DOCKER_TAG_COMMAND_TEMPLATE: List[str] = [
    DOCKER,
    "tag",
    "{image_id}",
    "{tag_name}",
]
DOCKER_PUSH_COMMAND_TEMPLATE: List[str] = [
    DOCKER,
    "push",
    "{image_id}",
]

GIT = "git"
GIT_SUBMODULE_STATUS_COMMAND: List[str] = [
    GIT,
    "submodule",
    "status",
]
GIT_VERSION_COMMAND: List[str] = [
    GIT,
    "describe",
    "--dirty",
    "--always",
    "--abbrev=12",
]
GIT_BRANCH_COMMAND: List[str] = [
    GIT,
    "branch",
    "--show-current",
]
GIT_REV_PARSE_COMMAND: List[str] = [
    GIT,
    "rev-parse",
    "HEAD",
]


def print_run(command: List[str], pretend: bool, return_stdout: bool = False, **kwargs):
    if "cwd" in kwargs:
        directory_piece = f' in directory "{kwargs["cwd"]}"'
    else:
        directory_piece = ""
    if pretend:
        print('Would run "{}"{}'.format(" ".join(command), directory_piece))
        return "<pretend>"
    else:
        print('Running "{}"{}'.format(" ".join(command), directory_piece))
        kwargs = kwargs.copy()
        if return_stdout:
            kwargs["stdout"] = PIPE
        proc = run(command, check=True, **kwargs)
        if return_stdout:
            return proc.stdout.strip().decode("utf-8")


def strip_v_from_version_number(tag: str) -> str:
    """
    :param tag: Tag name, with or without a leading 'v'
    :return: If a numeric version, strips one leading 'v' character. Otherwise
      `tag` is returned unchanged.

    >>> strip_v_from_version_number('v0.1')
    '0.1'
    >>> strip_v_from_version_number('v00..00')
    '00..00'
    >>> strip_v_from_version_number('v1.0-rc1')
    '1.0-rc1'
    >>> strip_v_from_version_number('version which should not change')
    'version which should not change'
    >>> strip_v_from_version_number('v.00..00')
    'v.00..00'
    """
    # TODO: consider requiring Python 3.8 for this
    m = VERSION_NUMBER_PATTERN.match(tag)
    if m:
        return m.group(1)
    else:
        return tag


def get_git_output(cwd: Path, command: List[str]) -> str:
    try:
        proc = run(command, cwd=cwd, stdout=PIPE, check=True)
        output = proc.stdout.decode("utf-8").strip()
        return output
    except Exception as e:
        # don't care too much; this is best-effort
        print("Caught", e)
        return ""


def get_git_info(cwd: Path) -> Dict[str, str]:
    # 2-tuples: (key for JSON metadata, command to run)
    commands = [
        ("branch", GIT_BRANCH_COMMAND),
        ("commit", GIT_REV_PARSE_COMMAND),
        ("version", GIT_VERSION_COMMAND),
    ]
    git_info = {key: get_git_output(cwd, command) for key, command in commands}
    print("Git information:")
    pprint(git_info)
    return git_info


def write_git_version(cwd: Path, dest_path: Path):
    # TODO: refactor
    git_version = get_git_info(cwd)["version"]
    print("Writing Git version", git_version, "to", dest_path)
    with open(dest_path, "w") as f:
        print(git_version, file=f)


def write_git_info(cwd: Path, dest_path: Path):
    # TODO: refactor
    git_info = get_git_info(cwd)
    print("Writing Git information to", dest_path)
    with open(dest_path, "w") as f:
        json.dump(git_info, f)


def read_images(directory: Path) -> List[Tuple[str, Path, Dict[str, Optional[str]]]]:
    """
    Reads an *ordered* list of Docker container/image information.
    Looks for 'docker_images.txt' in the given directory, and reads
    whitespace-separated lines. Piece 0 is the "base" name of the Docker
    container, without any tags, e.g. 'hubmap/codex-scripts', piece
    1 is the path to the matching Dockerfile, relative to this
    directory, and piece 2 is a string consisting of comma-separated
    options for the build.

    Lines starting with '#' are ignored.

    :param directory: directory containing `IMAGE_LIST_FILENAME`
    :return: List of (label, Dockerfile path, option set) tuples
    """
    images = []
    with open(directory / IMAGE_LIST_FILENAME) as f:
        for line in f:
            if line.startswith("#"):
                continue
            image, path, *rest = shlex.split(line)
            options = {}
            if rest:
                option_kv_list = rest[0].split(",")
                for kv_str in option_kv_list:
                    pieces = kv_str.split("=", 1)
                    value = pieces[1] if len(pieces) == 2 else None
                    options[pieces[0]] = value
            images.append((image, Path(path), options))
    return images


def check_submodules(directory: Path, ignore_missing_submodules: bool):
    submodule_status_output = (
        run(
            GIT_SUBMODULE_STATUS_COMMAND,
            stdout=PIPE,
            cwd=directory,
        )
        .stdout.decode("utf-8")
        .splitlines()
    )

    # name, commit
    uninitialized_submodules: Set[Tuple[str, str]] = set()

    for line in submodule_status_output:
        status_code, pieces = line[0], line[1:].split()
        if status_code == "-":
            uninitialized_submodules.add((pieces[1], pieces[0]))

    if uninitialized_submodules:
        message_pieces = ["Found uninitialized submodules:"]
        for name, commit in sorted(uninitialized_submodules):
            message_pieces.append(f"\t{name} (at commit {commit})")
        message_pieces.extend(
            [
                "Maybe you need to run",
                "\tgit submodule update --init",
                "(Override with '--ignore-missing-submodules' if you're really sure.)",
            ]
        )

        if not ignore_missing_submodules:
            raise RefusalToBuildException("\n".join(message_pieces))


def check_options(options: Dict[str, Optional[str]]):
    unknown_options = set(options) - SUPPORTED_OPTIONS
    if unknown_options:
        option_str = ", ".join(sorted(unknown_options))
        # TODO: decide whether this is an error
        warnings.warn(f"Unsupported Docker option(s): {option_str}")


def tag_image(image_id: str, tag_name: str, pretend: bool):
    docker_tag_command = [
        piece.format(
            image_id=image_id,
            tag_name=tag_name,
        )
        for piece in DOCKER_TAG_COMMAND_TEMPLATE
    ]
    print_run(docker_tag_command, pretend)
    print("Tagged image", image_id, "as", tag_name)


def build(
    tag_timestamp: bool,
    tag_git_describe: bool,
    tag: Optional[str],
    push: bool,
    ignore_missing_submodules: bool,
    pretend: bool,
    base_dir: Path = None,
):
    base_directory = Path() if base_dir is None else base_dir
    docker_images = read_images(base_directory)
    check_submodules(base_directory, ignore_missing_submodules)
    timestamp = datetime.now().strftime(TIMESTAMP_FORMAT)
    images_to_push = []
    for label_base, full_dockerfile_path, options in docker_images:
        label = f"{label_base}:latest"
        check_options(options)

        if GIT_VERSION_FILE_OPTION in options:
            git_version_file = Path(options[GIT_VERSION_FILE_OPTION])
            write_git_version(base_directory, git_version_file)

        if GIT_JSON_FILE_OPTION in options:
            git_json_file = Path(options[GIT_JSON_FILE_OPTION])
            write_git_info(base_directory, git_json_file)

        # TODO: seriously reconsider this; it feels wrong
        if BASE_DIR_BUILD_OPTION in options:
            if base_dir is not None:
                build_dir = base_dir
                full_dockerfile_path = base_dir / full_dockerfile_path
            else:
                build_dir = Path()
        else:
            build_dir = full_dockerfile_path.parent

        dockerfile_path = full_dockerfile_path.relative_to(build_dir)
        docker_build_command = [
            piece.format(
                label=label,
                dockerfile_path=dockerfile_path,
            )
            for piece in DOCKER_BUILD_COMMAND_TEMPLATE
        ]

        if PLATFORMS_OPTION in options:
            platforms_str = ",".join(options[PLATFORMS_OPTION].split("&"))
            docker_build_command.append(f"--platform={platforms_str}")

        image_id = print_run(docker_build_command, pretend, return_stdout=True, cwd=build_dir)
        images_to_push.append(label)
        print("Tagged image", image_id, "as", label)

        if tag_timestamp:
            timestamp_tag_name = f"{label_base}:{timestamp}"
            tag_image(image_id, timestamp_tag_name, pretend)
            images_to_push.append(timestamp_tag_name)

        if tag_git_describe:
            git_version = get_git_output(build_dir, GIT_VERSION_COMMAND)
            version_without_v = strip_v_from_version_number(git_version)
            version_tag_name = f"{label_base}:{version_without_v}"
            tag_image(image_id, version_tag_name, pretend)
            images_to_push.append(version_tag_name)

        if tag is not None:
            tag_name = f"{label_base}:{tag}"
            tag_image(image_id, tag_name, pretend)
            images_to_push.append(tag_name)

    if push:
        for image_id in images_to_push:
            docker_push_command = [
                piece.format(
                    image_id=image_id,
                )
                for piece in DOCKER_PUSH_COMMAND_TEMPLATE
            ]
            print_run(docker_push_command, pretend)


def main():
    p = ArgumentParser()
    p.add_argument(
        "--tag-timestamp",
        action="store_true",
        help="""
            In addition to tagging images as "latest", also tag with a
            timestamp in "YYYYMMDD-HHmmss" format. All images in "docker_images.txt"
            are tagged with the same timestamp.
        """,
    )
    p.add_argument(
        "--tag",
        help="""
            In addition to tagging images as "latest", also tag with the tag name
            provided. All images in "docker_images.txt" are tagged with the same tag name.
        """,
    )
    p.add_argument(
        "--tag-git-describe",
        action="store_true",
        help="""
            In addition to tagging images as "latest", also tag with the output of
            `git describe --dirty --always --abbrev=12`. All images in "docker_images.txt"
            are tagged with the same Git tag.
        """,
    )
    p.add_argument(
        "--push",
        action="store_true",
        help="""
            Push all built containers to Docker Hub, tagged as "latest" and with any
            additional tags specified via "--tag-timestamp" or "--tag=tag_name".
        """,
    )
    p.add_argument(
        "--ignore-missing-submodules",
        action="store_true",
        help="""
            Allow building Docker containers if "git submodule" reports that at least
            one submodule is uninitialized.            
        """,
    )
    p.add_argument(
        "--pretend",
        action="store_true",
        help="""
            Run in pretend mode: don't actually execute anything (building, tagging, pushing).
        """,
    )
    args = p.parse_args()

    try:
        build(
            tag_timestamp=args.tag_timestamp,
            tag_git_describe=args.tag_git_describe,
            tag=args.tag,
            push=args.push,
            ignore_missing_submodules=args.ignore_missing_submodules,
            pretend=args.pretend,
        )
    except RefusalToBuildException as e:
        print(ERROR_COLOR + "Refusing to build Docker containers, for reason:" + NO_COLOR)
        sys.exit(e.args[0])


if __name__ == "__main__":
    main()
