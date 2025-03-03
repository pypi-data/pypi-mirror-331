#! /usr/bin/env bash

# https://gazebosim.org/docs/harmonic/install_osx/
function blue_flie_gazebo_install() {
    local options=$1

    if [[ "$abcli_is_mac" == false ]]; then
        abcli_log_warning "only supported on Mac."
        return 0
    fi

    abcli_eval ,$options \
        brew tap osrf/simulation
    [[ $? -ne 0 ]] && return 1

    abcli_eval ,$options \
        brew install gz-harmonic
}

# https://gazebosim.org/docs/all/getstarted/
function abcli_install_blue_flie_gazebo() {
    abcli_git_clone https://github.com/gazebosim/gz-sim.git
}

abcli_install_module blue_flie_gazebo 1.1.1
