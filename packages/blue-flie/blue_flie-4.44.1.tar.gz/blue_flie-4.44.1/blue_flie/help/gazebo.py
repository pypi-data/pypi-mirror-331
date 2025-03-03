from typing import List

from blue_options.terminal import show_usage, xtra


def help_browse(
    tokens: List[str],
    mono: bool,
) -> str:
    options = xtra(
        "dryrun,~download,filename=<filename.sdf>,~gif,install,~pictures,~upload",
        mono=mono,
    )

    return show_usage(
        [
            "@gazebo",
            "browse",
            f"[{options}]",
            "[-|<object-name>]",
        ],
        "browse <object-name> in gazebo.",
        mono=mono,
    )


def help_ingest(
    tokens: List[str],
    mono: bool,
) -> str:
    options = xtra("dryrun,~upload", mono=mono)

    return show_usage(
        [
            "@gazebo",
            "ingest",
            f"[{options}]",
            "<example-name>",
            "[-|<object-name>]",
        ],
        "ingest <example-name> -> <object-name>.",
        mono=mono,
    )


def help_ingest_list(
    tokens: List[str],
    mono: bool,
) -> str:
    return show_usage(
        [
            "@gazebo",
            "ingest",
            "list",
        ],
        "list gazebo examples.",
        mono=mono,
    )


def help_install(
    tokens: List[str],
    mono: bool,
) -> str:
    options = xtra("dryrun", mono=mono)

    return show_usage(
        [
            "@gazebo",
            "install",
            f"[{options}]",
        ],
        "install gazebo.",
        mono=mono,
    )


help_functions = {
    "browse": help_browse,
    "ingest": {
        "": help_ingest,
        "list": help_ingest_list,
    },
    "install": help_install,
}
