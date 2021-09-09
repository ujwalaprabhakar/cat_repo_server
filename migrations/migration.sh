#!/bin/bash

# make the script fail when something fails
set -o errexit

username=""
password=""
hostname="localhost"
port="27017"

while getopts u:P:d:h:p:n: OPT
do
    case $OPT in
        "u" ) username="-u $OPTARG" ;;
        "P" ) password="-p $OPTARG" ;;
        "h" ) hostname="$OPTARG" ;;
        "p" ) port="$OPTARG" ;;
        "d" ) database="$OPTARG" ;;
        "n" ) number="$OPTARG" ;;
    esac
done

if [ -z "${database}" ]; then
    echo "ERROR: database is not specified"
    echo "$0 -d database"
    exit 1
fi

cd $(dirname $0)

if [ -z "${number}" ]; then
    for migration_file in *.js
    do
        echo "Running ${migration_file} on ${database}..."
        mongo ${username} ${password} --host ${hostname} --port ${port} \
            ${database} --eval "var ENVIRONMENT = '$ENVIRONMENT'" ${migration_file}
    done
else
    prefix=`echo ${number} | awk '{printf("%04d", $1)}'`
    mongo ${username} ${password} --host ${hostname} --port ${port} \
        ${database} --eval "var ENVIRONMENT = '$ENVIRONMENT'" ${prefix}_*.js
fi
