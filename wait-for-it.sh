#!/usr/bin/env bash
#   Use this script to test if a given TCP host/port are available
#   
#   Original script from: https://github.com/vishnubob/wait-for-it

set -e

TIMEOUT=15
QUIET=0
HOST=""
PORT=""
WAITHOST=""
WAITPORT=""

usage()
{
    cat << USAGE >&2
Usage:
    $0 host:port [-t timeout] [-q] [-- command args]
    -h HOST | --host=HOST       Host or IP under test
    -p PORT | --port=PORT       TCP port under test
                                Alternatively, you specify the host and port as host:port
    -t TIMEOUT | --timeout=TIMEOUT
                                Timeout in seconds, zero for no timeout
    -q | --quiet                Don't output any status messages
    -- COMMAND ARGS             Execute command with args after the test finishes
USAGE
    exit 1
}

wait_for()
{
    if [[ $QUIET -eq 1 ]]; then
        "$@" &> /dev/null
    else
        "$@"
    fi
}

while [ $# -gt 0 ]
do
    case "$1" in
        *:* )
        WAITHOST=$(echo $1 | cut -d : -f 1)
        WAITPORT=$(echo $1 | cut -d : -f 2)
        shift 1
        ;;
        -q | --quiet)
        QUIET=1
        shift 1
        ;;
        -t)
        TIMEOUT="$2"
        if [ "$TIMEOUT" = "" ]; then break; fi
        shift 2
        ;;
        --timeout=*)
        TIMEOUT="${1#*=}"
        shift 1
        ;;
        -h)
        HOST="$2"
        if [ "$HOST" = "" ]; then break; fi
        shift 2
        ;;
        --host=*)
        HOST="${1#*=}"
        shift 1
        ;;
        -p)
        PORT="$2"
        if [ "$PORT" = "" ]; then break; fi
        shift 2
        ;;
        --port=*)
        PORT="${1#*=}"
        shift 1
        ;;
        --)
        shift
        break
        ;;
        -*)
        usage
        ;;
        *)
        break
        ;;
    esac
done

if [ "$WAITHOST" = "" ]; then
    echo "Error: you need to provide a host and port to test."
    usage
fi

if [ "$WAITPORT" = "" ]; then
    echo "Error: you need to provide a port to test."
    usage
fi

WAITTIME=0
while [ $WAITTIME -lt $TIMEOUT ]; do
    if nc -z $WAITHOST $WAITPORT; then
        break
    fi
    WAITTIME=$((WAITTIME+1))
    sleep 1
done

if [ $WAITTIME -ge $TIMEOUT ]; then
    echo "Timeout occurred after waiting $TIMEOUT seconds for $WAITHOST:$WAITPORT"
    exit 1
fi

if [ $# -gt 0 ]; then
    exec "$@"
else
    exit 0
fi

