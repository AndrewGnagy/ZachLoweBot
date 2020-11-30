#!/bin/sh
cd "/home/andrew/GitHub/ZachLoweBot";
CWD="$(pwd)"
echo $CWD
/usr/bin/python3 zachlowebot.py > lowebot.log
