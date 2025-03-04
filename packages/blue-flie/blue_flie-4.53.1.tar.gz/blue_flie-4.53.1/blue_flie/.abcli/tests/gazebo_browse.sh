#! /usr/bin/env bash

function test_blue_flie_gazebo_browse() {
    local options=$1

    local object_name=sim-actor-2025-03-03-oanpvf

    abcli_eval ,$options \
        blue_flie_gazebo_browse \
        ~upload,$options \
        $object_name
}
