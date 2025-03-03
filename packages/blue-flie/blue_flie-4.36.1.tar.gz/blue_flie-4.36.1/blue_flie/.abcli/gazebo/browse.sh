#! /usr/bin/env bash

function blue_flie_gazebo_browse() {
    local options=$1
    local do_dryrun=$(abcli_option_int "$options" dryrun 0)
    local do_install=$(abcli_option_int "$options" install 0)
    local do_download=$(abcli_option_int "$options" download $(abcli_not $do_dryrun))
    local do_upload=$(abcli_option_int "$options" upload $(abcli_not $do_dryrun))
    local filename=$(abcli_option "$options" filename world.sdf)
    local ingest_pictures=$(abcli_option_int "$options" pictures 1)
    local generate_gif=$(abcli_option_int "$options" gif 1)

    if [[ "$do_install" == 1 ]]; then
        blue_flie_gazebo_install
        [[ $? -ne 0 ]] && return 1
    fi

    local object_name=$(abcli_clarify_object $2 gazebo-sim-$(abcli_string_timestamp_short))
    local object_path=$ABCLI_OBJECT_ROOT/$object_name
    mkdir -pv $object_path

    local browse_options=$3
    local do_server=$(abcli_option_int "$browse_options" server 0)
    local do_gui=$(abcli_option_int "$browse_options" gui $(abcli_not $do_server))

    [[ "$do_download" == 1 ]] &&
        abcli_download - $object_name

    local mode
    if [[ "$do_gui" == 1 ]]; then
        mode="-g"
    elif [[ "$do_server" == 1 ]]; then
        mode="-s"
    fi

    abcli_eval dryrun=$do_dryrun,path=$object_path \
        gz sim $mode $filename \
        "${@:4}"
    [[ $? -ne 0 ]] && return 1

    [[ "$ingest_pictures" == 1 ]] &&
        mv -v \
            $HOME/.gz/gui/pictures/*.png \
            $object_path

    if [[ "$generate_gif" == 1 ]]; then
        local scale
        for scale in 1 2 4; do
            abcli_gif ~download,~upload,dryrun=$do_dryrun \
                $object_name \
                --scale $scale
            [[ $? -ne 0 ]] && return 1
        done
    fi

    abcli_mlflow_tags_set \
        $object_name \
        contains=gazebo-simulation

    [[ "$do_upload" == 1 ]] &&
        abcli_upload - $object_name

    return 0
}
