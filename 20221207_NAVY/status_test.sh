#!/bin/bash

sshpass -p $3 ssh $2 -p 22 [[ -f $1 ]] && echo "File exists" || echo "File does not exist";

