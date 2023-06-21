#!/bin/sh
DIR="$( cd "$( dirname "$0" )" && pwd )"
input="tensors.txt"
if [ ! -e $DIR/downloads/ ]
then
  mkdir $DIR/downloads
fi

if [ ! -e $DIR/temp/ ]
then
  mkdir $DIR/temp
fi

while IFS= read -r line
do
  LAST_PORTION=${line##*/}
  if [ -e $DIR/downloads/$LAST_PORTION ]
  then
    echo "$LAST_PORTION found"
  else
    if [ -e $DIR/downloads/${LAST_PORTION%.*} ]
    then
        echo "${LAST_PORTION%.*} found"
    else
      BEFORE_GZ=${LAST_PORTION%.*}
      if [ -e $DIR/downloads/${BEFORE_GZ%.*}.mtx ]
      then 
        echo "${BEFORE_GZ%.*} found"
      else
        wget -P $DIR/downloads/ -q $line --show-progress
        if [ "${LAST_PORTION##*.}" = "gz" ]
        then
          # echo "$BEFORE_GZ"
          if [ "${BEFORE_GZ##*.}" = "tar" ]
          then
            tar xvzf $DIR/downloads/$LAST_PORTION -C $DIR/downloads
            mv $DIR/downloads/${BEFORE_GZ%.*}/${BEFORE_GZ%.*}.mtx $DIR/downloads
            rm $DIR/downloads/${BEFORE_GZ%.*}/ -r
            rm $DIR/downloads/$LAST_PORTION
          else
            gzip -d $DIR/downloads/$LAST_PORTION
          fi
        fi
      fi
      if [ "${LAST_PORTION##*.}" = "tgz" ]
      then
        tar xvzf $DIR/downloads/$LAST_PORTION -C $DIR/downloads
      fi
    fi
  fi
done < "$input"