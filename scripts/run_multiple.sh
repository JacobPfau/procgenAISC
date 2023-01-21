#!/bin/bash
labeled=(0.1 0.5 1 5)
for i in {0..9};
    do for ds in 0.1 0.5 1 5;
        do for ccs in 0 0.5;
            do for lr in 2e-5 8e-6 1e-6 5e-7;
                do cud="cuda:${1}";
                lab=${labeled[$1]}
                echo "$i $ds $ccs $lr $lab $cud";
                python run_experiment.py --preset "CLIP_ViT_special" --data "/data/do_not_modify/pandaGibbonAdversarial/" --user "${cud}" --labeled_scale  $lab --distinct_scale $ds --class_certainty_scale $ccs --lr $lr > /dev/null;
            done;
        done;
    done;
done
