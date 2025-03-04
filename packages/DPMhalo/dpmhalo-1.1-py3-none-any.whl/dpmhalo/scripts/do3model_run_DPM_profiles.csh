#!/bin/csh
# This is a script to make 3 model plots

set redshift = 0.00

set model = Model1
@ lm10 = 115 
rm -f 3models.z${redshift}.ls
while ($lm10 <= 150)
    set lm = `echo $lm10 | awk '{printf("%5.2f",$1/10)}'`
    if ($lm10 == 115) then
        set modellabel_bool = 1
    else
        set modellabel_bool = 0
    endif
    python run_DPM_profile.py $model $lm $redshift
    echo "ModelMFlexGNFW${model}.M${lm}.z${redshift}.dat $model $lm $redshift : 0 ${modellabel_bool}" >> 3models.z${redshift}.ls
    @ lm10+=5
end

set model = Model2
@ lm10 = 115 
while ($lm10 <= 150)
    set lm = `echo $lm10 | awk '{printf("%5.2f",$1/10)}'`
    if ($lm10 == 115) then
        set modellabel_bool = 1
    else
        set modellabel_bool = 0
    endif
    python run_DPM_profile.py $model $lm $redshift
    echo "ModelMFlexGNFW${model}.M${lm}.z${redshift}.dat $model $lm $redshift -- 0 ${modellabel_bool}" >> 3models.z${redshift}.ls
    @ lm10+=5
end

set model = Model3
@ lm10 = 115 
while ($lm10 <= 150)
    set lm = `echo $lm10 | awk '{printf("%5.2f",$1/10)}'`
    if ($lm10 == 115) then
        set modellabel_bool = 1
    else
        set modellabel_bool = 0
    endif
    python run_DPM_profile.py $model $lm $redshift
    echo "ModelMFlexGNFW${model}.M${lm}.z${redshift}.dat $model $lm $redshift - 1 ${modellabel_bool}" >> 3models.z${redshift}.ls
    @ lm10+=5
end

python plot_DPM_profiles.py 3models.z${redshift}.ls 
