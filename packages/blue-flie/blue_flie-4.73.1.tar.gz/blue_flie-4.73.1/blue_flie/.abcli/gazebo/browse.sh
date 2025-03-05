#! /usr/bin/env bash

function blue_flie_gazebo_browse() {
    local options=$1
    local do_dryrun=$(abcli_option_int "$options" dryrun 0)
    local do_install=$(abcli_option_int "$options" install 0)
    local do_download=$(abcli_option_int "$options" download $(abcli_not $do_dryrun))
    local do_upload=$(abcli_option_int "$options" upload $(abcli_not $do_dryrun))
    local ingest_pictures=$(abcli_option_int "$options" pictures 1)
    local generate_gif=$(abcli_option_int "$options" gif 1)

    if [[ "$do_install" == 1 ]]; then
        blue_flie_gazebo_install
        [[ $? -ne 0 ]] && return 1
    fi

    local object_name=$(abcli_clarify_object $2 gazebo-sim-$(abcli_string_timestamp_short))
    local object_path=$ABCLI_OBJECT_ROOT/$object_name
    mkdir -pv $object_path

    [[ "$do_download" == 1 ]] &&
        abcli_download - $object_name

    local filename=$(find "$object_path" -name '*.sdf' -print | head -n 1)
    filename=$(basename "$filename")
    filename=$(abcli_option "$options" filename $filename)

    if [[ "$abcli_is_github_workflow" == true ]]; then
        abcli_log_warning "will not run gazebo."
    else
        abcli_log "running gazebo: $filename"

        pushd $object_path >/dev/null
        gz sim -s $filename &
        pid=$!

        gz sim -g
        [[ $? -ne 0 ]] && return 1
        popd >/dev/null

        kill $pid
    fi

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
