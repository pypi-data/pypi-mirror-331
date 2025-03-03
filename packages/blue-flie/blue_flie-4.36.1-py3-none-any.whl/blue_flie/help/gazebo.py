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

    browse_options = "gui | server"

    return show_usage(
        [
            "@gazebo",
            "browse",
            f"[{options}]",
            "[-|<object-name>]",
            f"[{browse_options}]",
        ],
        "browse <object-name> in gazebo.",
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
    "install": help_install,
}
