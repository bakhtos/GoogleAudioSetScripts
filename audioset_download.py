# Code Contributor - Ankit Shah - ankit.tronix@gmail.com
# Modified - Alexander Bakhtin - alexander.bakhtin@tuni.fi
import time
import datetime
import itertools
import os
import sys
import multiprocessing
from multiprocessing import Pool

# Format audio - 16 bit Signed PCM audio sampled at 44.1kHz
def format_audio(input_audio_file,output_audio_file):
    temp_audio_file = output_audio_file[:-4] + '_temp.wav'
    cmdstring = "ffmpeg -loglevel panic -i %s -ac 1 -ar 44100 %s" %(input_audio_file,temp_audio_file)
    os.system(cmdstring)
    cmdstring1 = "sox %s -G -b 16 -r 44100 %s" %(temp_audio_file,output_audio_file)
    os.system(cmdstring1)
    cmdstring2 = "rm -rf %s" %(temp_audio_file)
    os.system(cmdstring2)

# Trim audio based on start time and duration of audio.
def trim_audio(input_audio_file,output_audio_file,start_time,duration):
    cmdstring = "sox %s %s trim %s %s" %(input_audio_file,output_audio_file,start_time,duration)
    os.system(cmdstring)

def multi_run_wrapper(args):
    return download_audio_method(*args)

#Method to download audio - Downloads the best audio available for audio id, calls the formatting audio function and then segments the audio formatted based on start and end time. 
def download_audio_method(line, csv_file):
    line = line[:-1]
    parts = line.split('_')
    query_id = '_'.join(parts[:-1])
    start_seconds = int(parts[-1])//1000
    end_seconds = start_seconds+10
    audio_duration = float(end_seconds) - float(start_seconds)
    url = "https://www.youtube.com/watch?v=" + query_id
    ex1 = ""
    try:

        output_folder = csv_file + "_downloaded" 
        formatted_folder = csv_file + "_formatted"
        segmented_folder = csv_file + "_segmented"

        path_to_download = os.path.join(output_folder, query_id+".wav")
        path_to_formatted_audio = os.path.join(formatted_folder, query_id+".wav")
        path_to_segmented_audio = os.path.join(segmented_folder, line+".wav")

        if not os.path.exists(path_to_download):
            cmdstring = "yt-dlp -f 'ba' -x --audio-format wav " + url + " -o '" + path_to_download + "'"
            os.system(cmdstring)
            format_audio(path_to_download,path_to_formatted_audio)
        else:
            print("File {} already exists.".format(query_id))

        #Trimming
        trim_audio(path_to_formatted_audio,path_to_segmented_audio,start_seconds,audio_duration)

    except Exception as ex:
        ex1 = str(ex) + ',' + str(query_id)

        print("Error is ---> " + str(ex))

    return ex1


#Download audio - Reads 3 lines of input csv file at a time and passes them to multi_run wrapper which calls download_audio_method to download the file based on id.
#Multiprocessing module spawns 3 process in parallel which runs download_audio_method. Multiprocessing, thus allows downloading process to happen in 40 percent of the time approximately to downloading sequentially - processing line by line of input csv file. 
def download_audio(csv_file, timestamp): 
    segments_info_file = open(csv_file, 'r')
    error_log = 'error' + timestamp + '.log'
    fo = open(error_log, 'a')
    #for line in tqdm(segments_info_file):
    while True:
        line1 = next(segments_info_file, None)
        line2 = next(segments_info_file, None)
        line3 = next(segments_info_file, None)
        lines_list = []
        lines_list.append((line1, csv_file))

        if line2 is not None:
            lines_list.append((line2, csv_file))
        if line3 is not None:
            lines_list.append((line3, csv_file))
        
        P = multiprocessing.Pool(3)

        exception = P.map(multi_run_wrapper,lines_list)
        for item in exception:
            if item:
                line = fo.writelines(str(item) +  '\n')
        P.close()
        P.join()
        if line2 is None or line3 is None: break
    segments_info_file.close()
    fo.close()

if __name__ == "__main__":
    if len(sys.argv) !=2:
        print('takes arg1 as csv file to downloaded')
    else:
        ts = time.time()
        timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y_%m_%d_%H_%M_%S')                   
        download_audio(sys.argv[1],timestamp)
        

