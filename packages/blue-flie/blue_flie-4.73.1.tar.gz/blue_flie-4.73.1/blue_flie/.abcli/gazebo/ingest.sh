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

    source_options=$2
    local example_name=$(abcli_option "$source_options" example)
    local fuel_name=$(abcli_option "$source_options" fuel)

    # either $example_name or $fuel_name is expected to be blank.
    local object_name=$(abcli_clarify_object $3 gazebo-sim-$example_name$fuel_name-$(abcli_string_timestamp_short))
    local object_path=$ABCLI_OBJECT_ROOT/$object_name
    mkdir -pv $object_path

    local tags="contains=gazebo-simulation"
    if [[ ! -z "$example_name" ]]; then
        example_name="${example_name%%.*}"
        abcli_log "ingesting: examples/$example_name -> $object_name ..."
        tags="$tags,example_name=$example_name"

        cp -v \
            $abcli_path_git/gz-sim/examples/worlds/$example_name.sdf \
            $object_path/
    elif [[ ! -z "$fuel_name" ]]; then
        fuel_name="${fuel_name%%.*}"
        abcli_log "ingesting: fuels/$fuel_name -> $object_name ..."
        tags="$tags,fuel_name=$fuel_name"

        local filename=$(find "$HOME/Downloads/" -name $fuel_name'*.zip' -print | head -n 1)
        filename=$(basename "$filename")
        if [[ -z "$filename" ]]; then
            abcli_log_error "fuel not found."
            return 1
        fi

        cp -v \
            $HOME/Downloads/$filename \
            $object_path/

        unzip $object_path/$filename \
            -d $object_path
    else
        abcli_log_error "neither example, nor fuel found"
        return 1
    fi

    abcli_mlflow_tags_set \
        $object_name \
        $tags

    [[ "$do_upload" == 1 ]] &&
        abcli_upload - $object_name

    local browse_options=$4
    local do_browse=$(abcli_option_int "$browse_options" browse 0)
    [[ "$do_browse" == 0 ]] &&
        return 0

    blue_flie_gazebo_browse \
        ~download,$browse_options \
        $object_name
}
