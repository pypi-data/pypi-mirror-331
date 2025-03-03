#! /usr/bin/env bash

function blue_flie_gazebo_ingest() {
    local options=$1

    local show_list=$(abcli_option_int "$options" list 0)
    if [[ "$show_list" == 1 ]]; then
        abcli_ls $abcli_path_git/gz-sim/examples/worlds
        return
    fi

    local do_dryrun=$(abcli_option_int "$options" dryrun 0)
    local do_upload=$(abcli_option_int "$options" upload $(abcli_not $do_dryrun))

    local example_name=${2:-actor}
    example_name="${example_name%%.*}"

    local object_name=$(abcli_clarify_object $3 gazebo-sim-$example_name-$(abcli_string_timestamp_short))
    local object_path=$ABCLI_OBJECT_ROOT/$object_name
    mkdir -pv $object_path

    abcli_log "ingesting: $example_name -> $object_name"

    cp -v \
        $abcli_path_git/gz-sim/examples/worlds/$example_name.sdf \
        $object_path/

    abcli_mlflow_tags_set \
        $object_name \
        contains=gazebo-simulation,example_name=$example_name

    [[ "$do_upload" == 1 ]] &&
        abcli_upload - $object_name

    return 0
}
