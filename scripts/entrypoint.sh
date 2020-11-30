#!/bin/sh
exec gunicorn -t 300 -w 4 -b 0.0.0.0:$PORT alertmanager_gchat_integration.__main__:app