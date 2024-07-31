# for uniform naming
# rename 1.tsv 1.variants.tsv *1.tsv
# rename _depths.txt .depth *_depths.txt

#!/bin/bash
my_func() {
    fn=$1
    depthfolder=$2
    output=$3

    fn_out=${fn##*/}
    baseName=${fn##*/}
    baseName=${baseName%.*}
    depthfile0="${depthfolder}${fn_out%.variants.tsv}.depth"
    output0="${output}${fn_out%.*}.demix.tsv"
    echo $fn
    echo $depthfile0
    echo $output0
    freyja demix $fn $depthfile0 --output $output0 --eps 0.0000001

}

export -f my_func
parallel -j 24 my_func ::: variants/* ::: depths/ ::: outputs/
freyja aggregate outputs/ --output agg_outputs.tsv