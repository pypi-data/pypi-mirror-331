# 🦋 blue-flie

🌀 `@flie` is an [`abcli`](https://github.com/kamangir/awesome-bash-cli) plugin for drone simulation and non-ROS robot control. See [blue-rover](https://github.com/kamangir/blue-rover) for ROS robots.

```bash
pip install blue-flie
```

```mermaid
graph LR
    gazebo_browse["@gazebo<br>browse -<br>&lt;object-name&gt;<br>gui|server"]

    gazebo_ingest_list["@gazebo<br>ingest<br>list"]

    gazebo_ingest["@gazebo<br>ingest -<br>&lt;example-name&gt;<br>&lt;object-name&gt;<br>browse"]

    examples["examples"]:::folder
    object["📁 object"]:::folder
    UI["🖥️ UI"]:::folder

    object --> gazebo_browse
    gazebo_browse --> object
    gazebo_browse --> UI

    gazebo_ingest_list --> examples 

    examples --> gazebo_ingest
    gazebo_ingest --> object
    gazebo_ingest --> gazebo_browse

    classDef folder fill:#999,stroke:#333,stroke-width:2px;
```

|   |   |
| --- | --- |
| [`swarm simulation`](./blue_flie/docs/gazebo.md) [![image](https://github.com/kamangir/assets/blob/main/gazebo-gif-1/gazebo-gif-1.gif?raw=true)](./blue_flie/docs/gazebo.md) Simulating harm/cost for drone swarms with [Gazebo](https://gazebosim.org/home). | [`Crazyflie`](./blue_flie/docs/crazyflie.md) [![image](https://www.bitcraze.io/images/documentation/overview/system_overview.jpg)](./blue_flie/docs/crazyflie.md) [Crazyflie 2.1 Brushless](https://www.bitcraze.io/products/crazyflie-2-1-brushless/) |
| [`blue-beast`](https://github.com/kamangir/blue-rover/blob/main/blue_rover/docs/blue-beast.md) [![image](https://github.com/waveshareteam/ugv_rpi/raw/main/media/UGV-Rover-details-23.jpg)](https://github.com/kamangir/blue-rover/blob/main/blue_rover/docs/blue-beast.md) [UGV Beast PI ROS2](https://www.waveshare.com/wiki/UGV_Beast_PI_ROS2) | [`blue-amo`](https://github.com/kamangir/blue-assistant/blob/main/blue_assistant/script/repository/blue_amo/README.md) [![image](https://github.com/kamangir/assets/blob/main/blue-amo-2025-02-03-zjs1ow/generating-frame-006.png?raw=true)](https://github.com/kamangir/blue-assistant/blob/main/blue_assistant/script/repository/blue_amo/README.md) Concept development with AI |

---


[![pylint](https://github.com/kamangir/blue-flie/actions/workflows/pylint.yml/badge.svg)](https://github.com/kamangir/blue-flie/actions/workflows/pylint.yml) [![pytest](https://github.com/kamangir/blue-flie/actions/workflows/pytest.yml/badge.svg)](https://github.com/kamangir/blue-flie/actions/workflows/pytest.yml) [![bashtest](https://github.com/kamangir/blue-flie/actions/workflows/bashtest.yml/badge.svg)](https://github.com/kamangir/blue-flie/actions/workflows/bashtest.yml) [![PyPI version](https://img.shields.io/pypi/v/blue-flie.svg)](https://pypi.org/project/blue-flie/) [![PyPI - Downloads](https://img.shields.io/pypi/dd/blue-flie)](https://pypistats.org/packages/blue-flie)

built by 🌀 [`blue_options-4.227.1`](https://github.com/kamangir/awesome-bash-cli), based on 🦋 [`blue_flie-4.60.1`](https://github.com/kamangir/blue-flie).
