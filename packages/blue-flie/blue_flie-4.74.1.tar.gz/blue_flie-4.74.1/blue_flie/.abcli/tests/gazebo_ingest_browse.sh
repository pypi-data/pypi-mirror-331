#! /usr/bin/env bash

function test_blue_flie_gazebo_ingest_browse() {
    local options=$1

    local object_name=test_blue_flie_gazebo_ingest_browse-$(abcli_string_timestamp_short)

    abcli_eval ,$options \
        blue_flie_gazebo_ingest \
        ~upload,$options \
        example=actor \
        $object_name \
        browse
}
