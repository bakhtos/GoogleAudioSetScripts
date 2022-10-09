# Audioset Scripts

A collection of scripts to analyze, prepare for and download Google's Audioset.
These scripts assume the usage of [Google's Audioset: Reformatted](https://github.com/bakhtos/GoogleAudioSetReformatted).
The files of the dataset need to be placed into `src/` folder.

## `audioset_download.py`

This file contains a function to download, format and segment a given YouTube audio, 
as well as a function to process an entire list of files in a parallelized way. 

This requires external packages `yt-dlp` and `sox`.

## `audioset_scripts.py`

This file contains scripts to counts files, classes and events in the dataset,
select top most occuring classes, filter the dataset by a list of files or classes,
as well as make tables of counts for several cases.

The only external files that are needed are `train_list.txt` and `eval_list.txt`,
which list the actually downloaded files. 

