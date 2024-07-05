#!/bin/sh
DIR="$( cd "$( dirname "$0" )" && pwd )"
if [ ! -e $DIR/downloads/ ]
then
    mkdir $DIR/downloads
fi

if [ ! -e $DIR/temp/ ]
then
    mkdir $DIR/temp
fi

if [ ! -e $DIR/test_configs/ ]
then
    mkdir $DIR/test_configs
fi

if [ ! -e $DIR/temporary_json/ ]
then
    mkdir $DIR/temporary_json
fi

if [ ! -e $DIR/tensors_stored/ ]
then
    mkdir $DIR/tensors_stored
fi

if [ ! -e $DIR/csv_results/ ]
then
    mkdir $DIR/csv_results
fi

if [ ! -e $DIR/pigeon/ ]
then
    mkdir $DIR/pigeon
fi

if [ ! -e $DIR/logs/ ]
then
    mkdir $DIR/logs
fi

if [ ! -e $DIR/plots/ ]
then
    mkdir $DIR/plots
fi

if [ ! -e $DIR/plots/fig8/ ]
then
    mkdir $DIR/plots/fig8
fi

if [ ! -e $DIR/plots/fig9/ ]
then
    mkdir $DIR/plots/fig9
fi

if [ ! -e $DIR/plots/fig10/ ]
then
    mkdir $DIR/plots/fig10
fi

if [ ! -e $DIR/plots/fig11/ ]
then
    mkdir $DIR/plots/fig11
fi

if [ ! -e $DIR/plots/fig12/ ]
then
    mkdir $DIR/plots/fig12
fi
