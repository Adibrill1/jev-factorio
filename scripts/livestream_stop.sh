#!/bin/bash
# Stop the agent side of the livestream. Also stop the stream in OBS
# (Stop Streaming) and, when fully done, run: fle cluster stop && colima stop
pkill -f "jev_factorio.live" && echo "agent loop stopped" || echo "agent loop was not running"
pkill -f "caffeinate -dims" && echo "caffeinate stopped" || echo "caffeinate was not running"
echo "Next: in OBS press Stop Streaming. Fully done? run: fle cluster stop && colima stop"
