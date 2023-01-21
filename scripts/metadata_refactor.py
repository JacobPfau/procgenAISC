"""
Script for converting from the old to new metadata file formats.

Usage:
    python3.9 metadata_refactor.py /data/dataset/metadata.json

Old format:

{
  "n_features": 2,
  "true_feat_idx": 0,
  "classes": [
    [
      "panda",
      "gibbon"
    ],
    [
      "panda",
      "gibbon"
    ]
  ],
  "folder_label_dict": {
    "AnPAdP": [
      "panda",
      "panda"
    ],
    "AnGAdG": [
      "gibbon",
      "gibbon"
    ],
    "AnPAdG": [
      "panda",
      "gibbon"
    ],
    "AnGAdP": [
      "gibbon",
      "panda"
    ]
  }
}

New format:

{
    "training_folders": {
        "labeled/diag/AnGAdG/" : [[1, 1], [true, true]],
        "labeled/diag/AnPAdP/" : [[0, 0], [true, true]],
        "unlabeled/diag/AnGAdG/" : [[1, 1], [false, false]],
        "unlabeled/diag/AnPAdP/" : [[0, 0], [false, false]],
        "unlabeled/cross/AnGAdP/" : [[1, 1], [false, false]],
        "unlabeled/cross/AnPAdG/" : [[1, 0], [false, false]]
    },
    "validation_folders": {
        "val/diag/AnGAdG/" : [[1,1]],
        "val/diag/AnPAdP/" : [[0,0]],
        "val/cross/AnGAdP/" : [[1,0]],
        "val/cross/AnPAdG/" : [[0,1]]
    },
    "testing_folders": {
        "test/diag/AnGAdG/" : [[1,1]],
        "test/diag/AnPAdP/" : [[0,0]],
        "test/cross/AnGAdP/" : [[1,0]],
        "test/cross/AnPAdG/" : [[0,1]]
    }
}
"""

import sys
import json
from typing import Union, Optional

def _get_folder_labels(oldj):
    classes_map: dict[str, int] = {c:i for i, c in enumerate(oldj['classes'][0])}
    diag_folders: dict[str, list[int]] = {}
    cross_folders: dict[str, list[int]] = {}
    for folder, label_names in oldj['folder_label_dict'].items():
        labels: list[int] = []
        for label_name in label_names:
            labels.append(classes_map[label_name])
        if labels[0] == labels[1]:
            diag_folders[folder] = labels
        else:
            cross_folders[folder] = labels
    return diag_folders, cross_folders 


def _get_folders(subset: str, diag: 'dict[str, list[int]]', cross: 'dict[str, list[int]]'={}, known_labels:'Optional[list[bool]]'=None):
    folders: dict[str, list[Union[list[int], list[bool]]]]  = {}
    for f, l in diag.items():
        labels: list[Union[list[int], list[bool]]] = [l]
        if known_labels is not None:
            labels.append(known_labels)
        folders[f'{subset}/diag/{f}'] = labels
    for f, l in cross.items():
        labels = [l]
        if known_labels is not None:
            labels.append(known_labels)
        folders[f'{subset}/cross/{f}'] = labels
    return folders


if __name__ == '__main__':
    metadata_path = sys.argv[1]

    with open(metadata_path, 'r') as oldf:
        oldj = json.load(oldf)

    diag_folders, cross_folders = _get_folder_labels(oldj)

    labeled_folders = _get_folders('labeled', diag_folders, known_labels=[True, True])
    unlabeled_folders = _get_folders('unlabeled', diag_folders, cross=cross_folders, known_labels=[False, False])
    val_folders = _get_folders('val', diag_folders, cross=cross_folders)
    test_folders = _get_folders('test', diag_folders, cross=cross_folders)

    newj = {
        'training_folders': labeled_folders | unlabeled_folders,
        'validation_folders': val_folders,
        'testing_folders': test_folders,
    }
    with open(metadata_path, 'w') as newf:
        json.dump(newj, newf)
