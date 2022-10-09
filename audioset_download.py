# Code Contributor - Ankit Shah - ankit.tronix@gmail.com
# Modified - Alexander Bakhtin - alexander.bakhtin@tuni.fi
import os
import sys
import argparse
from multiprocessing import Pool

def download_audio(segment_id, dataset_name, clip_length=10000, sample_rate=44100, bits=16, channels=1):
    ''' Download, reformat and trim audio from YouTube.

    Saves the original downloaded audio in best quality in wav format, 
    audio formatted in quality (bits, channels, sample rate) specified by user,
    and audio cut to specified segment.

    Parameters
    __________
    segment_id : str
        A string in the format 'YTID_STARTTIME', where YT_ID is the YouTube ID
        of the video and STARTTIME is the time stamp (in ms) to trim video from.
    dataset_name : str
        Name of the download, used to create download folders: f'{dataset_name}_downloaded',
        f'{dataset_name}_formatted' and f'{dataset_name}_segmented'.
    clip_length : int, optional (default 10000)
        Length (in ms) of clip to trim from the STARTTIME specified in input_file.
        NOTE: if the resulting clip is actually shorter, it will NOT be extended by SOX.
    sample_rate : int, optional (default 44100)
        Sample rate (in Hz) to resample the downloaded audios into.
        (Passed to sox -s)
    bits : int, optional (default 16)
        Quality of audiosteam to convert into. (Passed to sox -b)
    channels : int, optional (default 1)
        Number of channels to convert audio into. (Passed to sox -c)
    '''
    

    parts = segment_id.split('_')
    query_id = '_'.join(parts[:-1])

    start_seconds = int(parts[-1])//1000
    clip_length = clip_length//1000

    url = "https://www.youtube.com/watch?v=" + query_id

    download_folder = dataset_name + "_downloaded" 
    formatted_folder = dataset_name + "_formatted"
    segmented_folder = dataset_name + "_segmented"

    path_to_download = os.path.join(download_folder, f"Y{query_id}.wav")
    path_to_formatted_audio = os.path.join(formatted_folder, f"Y{query_id}.wav")
    path_to_segmented_audio = os.path.join(segmented_folder, f"Y{segment_id}.wav")

    try:
        print(f"{query_id}: Downloading...")
        if os.path.exists(path_to_download):
            print(f"{query_id}: Downloaded file already exists.")
        else:
            cmdstring = f"yt-dlp -f 'ba' -x --audio-format wav {url} -o '{path_to_download}'"
            os.system(cmdstring)
        
        print(f"{query_id}: Formatting...")
        if os.path.exists(path_to_formatted_audio):
            print(f"{query_id}: Formatted file already exists.")
        else:
            cmdstring = f"sox {path_to_download} -G -c {bits} -b {channels} -r {sample_rate} {path_to_formatted_audio}"
            os.system(cmdstring)

        print(f"{query_id}: Trimming...")
        if os.path.exists(path_to_segmented_audio):
            print(f"{query_id}: Trimmed file already exists.")
        else:
            if clip_length == 0:
                cmdstring = f"sox {path_to_formatted_audio} {path_to_segmented_audio} trim {start_seconds}"
            else:
                cmdstring = f"sox {path_to_formatted_audio} {path_to_segmented_audio} trim {start_seconds} {clip_length}"
            os.system(cmdstring)

    except Exception as ex:
        print(f"{query_id}: Error - {str(ex)}")


def parallelize_download(input_file,num_workers=None, clip_length=10000,
                         sample_rate=44100, bits=16, channels=1):
    ''' Parallelize the task of downloading data from YouTube.

    Parameters
    __________
    input_file : str
        A text file (with or without '.txt' suffix, which one video to download
        on each line in the format 'YTID_STARTTIME', where YT_ID is the YouTube ID
        of the video and STARTTIME is the time stamp (in ms) to trim video from.
        NOTE: the input file will be openned by Python for the whole execution
        of the program.
    num_workers : int, optional (default None)
        Amount of processes (downloads) to spawn using Pool().
    clip_length : int, optional (default 10000)
        Length (in ms) of clip to trim from the STARTTIME specified in input_file.
        NOTE: if the resulting clip is actually shorter, it will NOT be extended by SOX.
    sample_rate : int, optional (default 44100)
        Sample rate (in Hz) to resample the downloaded audios into.
        (Passed to sox -s)
    bits : int, optional (default 16)
        Quality of audiosteam to convert into. (Passed to sox -b)
    channels : int, optional (default 1)
        Number of channels to convert audio into. (Passed to sox -c)
    '''
    
    dataset_name = input_file.removesuffix('.txt')
    with open(input_file, 'r') as segments_info_file:
        while True:
            lines_list = []
            last_loop = False
            for i in range(num_workers):
                line = next(segments_info_file, None)
                if line is not None: lines_list.append((line.removesuffix('\n'),
                                                        dataset_name,
                                                        clip_length,
                                                        sample_rate,
                                                        bits, channels))
                last_loop = line is None
        
            with Pool(num_workers) as P:
                P.starmap(download_audio,lines_list)
            if last_loop: break

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', '-i', type=str, required=True,
                        help='List of YouTube file-intervals to be downloaded,'
                        ' in format YTID_STARTTIME, one per line')
    parser.add_argument('--num_workers', '-n', type=int, default=None,
                        help='Amount of processes/workers to pass to Pool()')
    parser.add_argument('--clip_length', type=int, default=10000,
                        help='Length (in ms) of the clip to be extracted from the starting timestamp')
    parser.add_argument('--sample_rate', '-s', type=int, default=44100,
                        help="Sample rate (in Hz), passed to the sox -s parameter")
    parser.add_argument('--bits', '-b', type=int, default=16,
                        help="Quality of the bitstream, passed to the sox -b parameter")
    parser.add_argument('--channels', '-c', type=int, default=1,
                        help="Amount of channels to keep, passed to the sox -c parameter")
    args = parser.parse_args()
    parallelize_download(args.input,args.num_workers, args.clip_length,
                         args.sample_rate, args.bits, args.channels)
