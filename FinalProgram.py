# OM OM OM
import sounddevice as sd
import numpy as np
import threading
import time
from scipy.signal import butter, lfilter
from collections import deque

# Our Libraries
import FBImageWrite2 as FBIW  # To update the display


# Starting sound classification
print("Starting Sound Classification")
# import FinalYamnet as SC

# thread = threading.Thread(target=SC.RunSoundClassification, daemon=True)
# thread.start()





# ========================================================== YAMNetClassification Start ====================================================
import ModifiedYAMNetClassification as SC

SAMPLE_RATE = 16000
BUFFER_DURATION = 5  # seconds
audio_buffer = deque(maxlen=int(BUFFER_DURATION * 44100))

# ========================================================== YAMNetClassification Start ====================================================






# Measured average difference between mics
CALIBRATION_OFFSET_DB_MIC1 = -2  # Adjust if one mic is always louder
CALIBRATION_OFFSET_DB_MIC2 = 10  # 10

# Difference Threshold
diffThreshold = 1

# To control display update frequency
minPassesBeforeNextDisplayUpdate = 50
numberOfPassesAfterLastDisplayUpdate = minPassesBeforeNextDisplayUpdate - 5
lastDirection = 'Center'
DirectionCountsInTheInterval = {'Left': 0, 'Center': 0, 'Right': 0}

# Store latest dB values from both mics
mic_levels = {"Mic 1": -np.inf, "Mic 2": -np.inf}
lock = threading.Lock()


def butter_filter(cutoff, fs, btype='low', order=5):
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    b, a = butter(order, normal_cutoff, btype=btype, analog=False)
    return b, a

def apply_filter(data, cutoff, fs, btype='low', order=5):
    b, a = butter_filter(cutoff, fs, btype, order)
    return lfilter(b, a, data)


def get_db(indata):
    rms = np.linalg.norm(indata) * 10  # Scale factor to improve readings
    return 20 * np.log10(rms) if rms > 0 else -np.inf

def mic_stream(device_index, mic_name, calibration_offset=0, isPreferredAudioDataCollector=False):
    global numberOfPassesAfterLastDisplayUpdate, lastDirection, DirectionCountsInTheInterval
    def callback(indata, frames, time_info, status):
        global numberOfPassesAfterLastDisplayUpdate, lastDirection, DirectionCountsInTheInterval, audio_buffer
        
        # ========================================================== YAMNetClassification Start ====================================================

        if isPreferredAudioDataCollector:
            audio_buffer.extend(indata[:, 0])
            if len(audio_buffer) >= 44100 * BUFFER_DURATION:
                data = np.array(audio_buffer)
                SC.process_audio_with_yamnet(data.copy(), 44100)
                audio_buffer.clear()

        # ========================================================== YAMNetClassification Start ====================================================

        # Apply high-pass filter to remove low-frequency hum (e.g., <100Hz)
        filtered_data = apply_filter(indata[:, 0], cutoff=100, fs=48000, btype='high')

        # Apply low-pass filter to remove high-frequency noise (e.g., >8000Hz)
        filtered_data = apply_filter(filtered_data, cutoff=8000, fs=48000, btype='low')

        db = get_db(filtered_data) + calibration_offset

        # db = get_db(indata[:, 0]) + calibration_offset
        
        with lock:
            mic_levels[mic_name] = db
            db1 = mic_levels["Mic 1"]
            db2 = mic_levels["Mic 2"]

        # Estimate direction based on dB difference
        diff = db1 - db2
        direction = ""
        if abs(diff) > diffThreshold:  # Threshold in dB for meaningful difference
            if diff > 0:
                direction = "Left"
            else: 
                direction = "Right"

            '''
            Complete Left - > 5
            Center - -5 < x < 5
            Complete Right -> < -5
            '''

            if diff >= 4.5:
                direction = "Left"
            elif -4.2 < diff < 4.5:
                direction = "Center"
            elif diff < -4.2:
                direction = "Right"

            # print(f"Mic 1: {db1:.2f} dB | Mic 2: {db2:.2f} dB | Difference: {diff:.2f} | {direction}")
            # print(direction)

            DirectionCountsInTheInterval[direction] += 1
            numberOfPassesAfterLastDisplayUpdate += 1
            if numberOfPassesAfterLastDisplayUpdate >= minPassesBeforeNextDisplayUpdate:
                numberOfPassesAfterLastDisplayUpdate = 0

                # Finding the mostDirection
                maxDirection = max(DirectionCountsInTheInterval, key=DirectionCountsInTheInterval.get)

                # print(f"Writing: {maxDirection}")
                # print(f"Classified here is {SC.classifiedAlert}")
                FBIW.WriteToDisplay(maxDirection, SC.classifiedAlert)
                # FBIW.WriteToDisplay(maxDirection)
                DirectionCountsInTheInterval = {'Left': 0, 'Center': 0, 'Right': 0}
                # lastDirection = maxDirection

        # if db1 > db2:
        #     print(f"Mic 1: {db1:.2f} dB | Mic 2: {db2:.2f} dB | {'Left'}")
        # else:
        #     print(f"Mic 1: {db1:.2f} dB | Mic 2: {db2:.2f} dB | {'Right'}")

    with sd.InputStream(device=device_index, channels=1, samplerate=48000, blocksize=1024, callback=callback):
        print(f"{mic_name} stream started.")
        while True:
            time.sleep(0.1)  # Reduce CPU usage

# Update these to your actual device indices (use sd.query_devices() to find them)
mic1_device_index = 4
mic2_device_index = 5

mic1_thread = threading.Thread(target=mic_stream, args=(mic1_device_index, "Mic 1", CALIBRATION_OFFSET_DB_MIC1, True))
mic2_thread = threading.Thread(target=mic_stream, args=(mic2_device_index, "Mic 2", CALIBRATION_OFFSET_DB_MIC2))

mic1_thread.start()
mic2_thread.start()

# print(sd.query_devices())
