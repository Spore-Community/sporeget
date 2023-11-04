#!/bin/bash

version="v0.1-20231104"

links_output=$(python sporeget.py "$@")
links_exit_code=$?

if [ $links_exit_code -ne 0 ]; then
    echo "$links_output"
fi

if [ $links_exit_code -eq 0 ]; then
    command=$(echo $@ | cut -d ' ' -f 1)
    arg=$(echo $@ | cut -d ' ' -f 2)
    workdir=$(pwd)
    timestamp=$(date +"%Y%m%d%H%M%S")
    itemname="sporeget-$command-$arg-$timestamp"
    inputfile="$itemname.txt"

    useragent=$(cat useragent.txt)
    warcdir="saved"
    warcfile="$itemname"
    wait="0.5"
    waitretry="5"
    timeout="60"
    tries="3"

    if ! [[ -d "$workdir/$warcdir" ]]; then
        mkdir "$workdir/$warcdir"
    fi
    cd "$workdir/$warcdir"
    touch "$inputfile"
    echo "$links_output" > "$inputfile"
    wgetargs=(
        "--user-agent=$useragent"
        "--header=Connection: keep-alive"
        "--reject-reserved-subnets"
        "--warc-dedup-url-agnostic"
        "--warc-file=$warcfile"
        #"--warc-item-name=$itemname"
        "--warc-header=x-sporeget-version: $version"
        "--warc-cdx"
        "--no-check-certificate" #Spore website seems to have problems with SSL certificates sometimes.
        "--content-on-error"
        "--wait=$wait"
        "--waitretry=$waitretry"
        "--timeout=$timeout"
        "--tries=$tries"
        "--retry-connrefused"
        "--no-cookies"
        "--no-parent"
        "--no-http-keep-alive"
        "--delete-after"
        #"--page-requisites"

        "--domains=www.spore.com,static.spore.com,pollinator.spore.com"
        "--input-file=$inputfile"
    )
    wget-lua "${wgetargs[@]}" 2>&1
    cd $workdir
fi
