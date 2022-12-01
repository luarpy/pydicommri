#!/bin/bash

main(){
    local dir_name="$(ls -al | grep -i "env" | rev | cut -d' ' -f1 | rev)"
    printf %s\\n "Enviroment dir: $dir_name"
    source "$dir_name/bin/activate"

    printf %s\\n "Installed packages:"
    pip list
}

[ $BASH_SOURCE[0] == "$0" ] && main