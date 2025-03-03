import os

from blue_options.help.functions import get_help
from blue_objects import file, README

from blue_flie import NAME, VERSION, ICON, REPO_NAME
from blue_flie.help.functions import help_functions


items = README.Items(
    [
        {
            "name": "swarm simulation",
            "marquee": "https://github.com/kamangir/assets/blob/main/gazebo-gif-1/gazebo-gif-1.gif?raw=true",
            "description": "Simulating harm/cost for swarms of AI IEDs with [Gazebo](https://gazebosim.org/home).",
            "url": "./blue_flie/docs/gazebo.md",
        },
        {
            "name": "Crazyflie",
            "marquee": "https://www.bitcraze.io/images/documentation/overview/system_overview.jpg",
            "description": "[Crazyflie 2.1 Brushless](https://www.bitcraze.io/products/crazyflie-2-1-brushless/)",
            "url": "./blue_flie/docs/crazyflie.md",
        },
        {
            "name": "blue-beast",
            "marquee": "https://github.com/waveshareteam/ugv_rpi/raw/main/media/UGV-Rover-details-23.jpg",
            "description": "[UGV Beast PI ROS2](https://www.waveshare.com/wiki/UGV_Beast_PI_ROS2)",
            "url": "https://github.com/kamangir/blue-rover/blob/main/blue_rover/docs/blue-beast.md",
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
                "cols": 2,
                "path": "..",
            },
            {
                "path": "docs/crazyflie.md",
            },
        ]
        + [
            {
                "path": f"docs/gazebo{suffix}.md",
            }
            for suffix in ["", "-01", "-02"]
        ]
    )
