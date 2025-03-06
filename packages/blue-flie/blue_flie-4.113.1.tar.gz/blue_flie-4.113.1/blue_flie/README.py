import os

from blue_options.help.functions import get_help
from blue_objects import file, README

from blue_flie import NAME, VERSION, ICON, REPO_NAME
from blue_flie.fpv import items as fpv_items
from blue_flie.fpv import list_of_columns as fpv_columns
from blue_flie.help.functions import help_functions


items = README.Items(
    [
        {
            "name": "Swarm Simulation",
            "marquee": "https://github.com/kamangir/assets/blob/main/gazebo-gif-1/gazebo-gif-1.gif?raw=true",
            "description": "Simulating harm/cost for drone swarms with [Gazebo](https://gazebosim.org/home).",
            "url": "./blue_flie/docs/gazebo.md",
        },
        {
            "name": "FPV",
            "marquee": "https://github.com/kamangir/assets/raw/main/blue-flie/fpv/7-in.png?raw=true",
            "description": "FPVs available in the market",
            "url": "./blue_flie/docs/fpv.md",
        },
        {
            "name": "blue Crazy",
            "marquee": "https://www.bitcraze.io/images/documentation/overview/system_overview.jpg",
            "description": "based on [Crazyflie 2.1 Brushless](https://www.bitcraze.io/products/crazyflie-2-1-brushless/)",
            "url": "./blue_flie/docs/blue-crazy.md",
        },
        {
            "name": "blue Beast",
            "marquee": "https://github.com/waveshareteam/ugv_rpi/raw/main/media/UGV-Rover-details-23.jpg",
            "description": "based on [UGV Beast PI ROS2](https://www.waveshare.com/wiki/UGV_Beast_PI_ROS2)",
            "url": "https://github.com/kamangir/blue-rover/blob/main/blue_rover/docs/blue-beast.md",
        },
        {
            "name": "blue Amo",
            "marquee": "https://github.com/kamangir/assets/blob/main/blue-amo-2025-02-03-zjs1ow/generating-frame-006.png?raw=true",
            "description": "Concept development with AI",
            "url": "https://github.com/kamangir/blue-assistant/blob/main/blue_assistant/script/repository/blue_amo/README.md",
        },
    ]
)


def build():
    return all(
        README.build(
            items=readme.get("items", []),
            cols=readme.get("cols", 3),
            path=os.path.join(file.path(__file__), readme["path"]),
            ICON=ICON,
            NAME=NAME,
            VERSION=VERSION,
            REPO_NAME=REPO_NAME,
            help_function=lambda tokens: get_help(
                tokens,
                help_functions,
                mono=True,
            ),
        )
        for readme in [
            {
                "items": items,
                "path": "..",
            },
            {
                "items": fpv_items,
                "cols": len(fpv_columns),
                "path": "docs/fpv.md",
            },
        ]
        + [
            {
                "path": f"docs/{suffix}.md",
            }
            for suffix in ["gazebo", "blue-crazy"]
            + ["gazebo-{:02d}".format(index + 1) for index in range(3)]
        ]
    )
