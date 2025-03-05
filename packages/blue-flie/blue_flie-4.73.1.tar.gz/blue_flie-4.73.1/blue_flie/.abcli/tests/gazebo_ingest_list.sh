#! /usr/bin/env bash

function test_blue_flie_gazebo_ingest_list() {
    local options=$1

    abcli_eval ,$options \
        "blue_flie_gazebo_ingest list ${@:2}"
}
