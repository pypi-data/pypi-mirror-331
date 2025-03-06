from typing import List

from blue_options.terminal import show_usage, xtra

example_details = {
    "examples: https://github.com/gazebosim/gz-sim/examples/worlds/": [],
}

fuel_details = {
    "fuel: https://app.gazebosim.org/fuel": [],
}


def browse_options(
    mono: bool,
    cascade: bool = False,
):
    return "".join(
        [
            xtra(
                "dryrun,",
                mono=mono,
            ),
            (
                ""
                if cascade
                else xtra(
                    "~download,",
                    mono=mono,
                )
            ),
            xtra(
                "filename=<filename.sdf>,~gif,install,~pictures,~upload",
                mono=mono,
            ),
        ]
    )


def help_browse(
    tokens: List[str],
    mono: bool,
) -> str:

    return show_usage(
        [
            "@gazebo",
            "browse",
            f"[{browse_options(mono=mono)}]",
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

    source_options = "example=<example-name> | fuel=<fuel-name>"

    return show_usage(
        [
            "@gazebo",
            "ingest",
            f"[{options}]",
            f"[{source_options}]",
            "[-|<object-name>]",
            "[browse,{}]".format(
                browse_options(
                    mono=mono,
                    cascade=True,
                )
            ),
        ],
        "ingest <example-name> -> <object-name>.",
        {
            **example_details,
            **fuel_details,
        },
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
        {
            **example_details,
        },
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
