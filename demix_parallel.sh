# for uniform naming
cd variants/
rename 1.tsv 1.variants.tsv *1.tsv
cd ../depths/
rename _depths.txt .depth *_depths.txt
cd ..
freyja update --outdir . 
freyja update
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
    freyja demix $fn $depthfile0 --output $output0 --eps 0.0000001 --autoadapt

}

export -f my_func
parallel -j 5 my_func ::: variants/* ::: depths/ ::: outputs/
freyja aggregate outputs/ --output agg_outputs.tsv

python polish_outputs.py
python calc_relgrowthrates.py