#!/bin/bash

while [ TRUE ];
    ls /params > to_delete.txt;
    do sleep 2400;
    for i in $(cat to_delete.txt); do
        rm -f /params/${i};
    done
done