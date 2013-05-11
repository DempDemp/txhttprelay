#!/bin/bash

### BEGIN INIT INFO
# Provides:          txhttprelay
# Required-Start:    $all
# Required-Stop:     $all
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Starts twistd daemon and loads txhttprelay
# Description:       Starter for txhttprelay
### END INIT INFO

TAC="txhttprelay.tac"
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

DAEMON="/usr/bin/twistd"
PIDFILE="$DIR/txhttprelay.pid"
DAEMON_OPTS="--pidfile=$PIDFILE -y $DIR/$TAC"

if [ ! -x $DAEMON ]; then
    echo "ERROR: Can't execute $DAEMON."
    exit 1
fi

start_service() {
    echo -n " * Starting $TAC... "
    start-stop-daemon -Sq -p $PIDFILE -x $DAEMON -- $DAEMON_OPTS
    e=$?
    if [ $e -eq 1 ]; then
        echo "already running"
        return
    fi
    if [ $e -eq 255 ]; then
        echo "couldn't start"
        return
    fi
    echo "done"
}

stop_service() {
    echo -n " * Stopping $TAC... "
    start-stop-daemon -Kq -R 10 -p $PIDFILE
    e=$?
    if [ $e -eq 1 ]; then
        echo "not running"
        return
    fi
    echo "done"
}

case "$1" in
    start)
        start_service
        ;;
    stop)
        stop_service
        ;;
    restart)
        stop_service
        start_service
        ;;
    *)
        echo "Usage: $0 {start|stop|restart}" >&2
        exit 1   
    ;;
esac

exit 0
