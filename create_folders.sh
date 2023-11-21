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

    if [ ! -e $DIR/test_outputs/ ]
    then
        mkdir $DIR/test_outputs
    fi

    if [ ! -e $DIR/test_configs/ ]
    then
        mkdir $DIR/test_configs
    fi

    if [ ! -e $DIR/tensors_stored/ ]
    then
        mkdir $DIR/tensors_stored
    fi

    if [ ! -e $DIR/logs/ ]
    then
        mkdir $DIR/logs
    fi
    
    if [ ! -e $DIR/temporary_json/ ]
    then
        mkdir $DIR/temporary_json
    fi