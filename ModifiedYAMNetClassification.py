# OM OM OM
import sounddevice as sd
import numpy as np
from collections import deque
import tensorflow as tf
import tensorflow_hub as hub
import pandas as pd
import scipy.signal

# Load model
yamnet_model = hub.load('https://tfhub.dev/google/yamnet/1')
class_map = pd.read_csv('yamnet_class_map.csv')
class_names = class_map['display_name'].to_list()

SAMPLE_RATE = 16000
BUFFER_DURATION = 5  # seconds
DANGEROUS_CLASSES = ['Gunshot', 'Glass', 'Siren', 'Screaming', 'Explosion', 'Shatter', 'Glass']
FILTER_CLASSES = ['Silence', 'Speech', 'Music']

audio_buffer = deque(maxlen=int(BUFFER_DURATION * 44100))

classifiedAlert = ''

def process_audio_with_yamnet(audio_data, sample_rate):
    global classifiedAlert


    if sample_rate != SAMPLE_RATE:
        audio_data = scipy.signal.resample(audio_data, int(len(audio_data) * SAMPLE_RATE / sample_rate))
    waveform = tf.reshape(tf.convert_to_tensor(audio_data, dtype=tf.float32), [-1])
    scores, embeddings, spectrogram = yamnet_model(waveform)
    max_scores = tf.reduce_max(scores, axis=0).numpy()
    top5_i = np.argsort(max_scores)[-5:][::-1]
    top5_labels = [class_names[i] for i in top5_i]
    top5_scores = max_scores[top5_i]

    # print("\n🔊 Top 5 Predictions:")
    # for label, score in zip(top5_labels, top5_scores):
    #     print(f"{label}: {score * 100:.2f}%")

    filtered_labels = [label for label in top5_labels if label not in FILTER_CLASSES]

    classifiedAlert = ''
    for label in filtered_labels:
        # if any(danger.lower() in label.lower() for danger in DANGEROUS_CLASSES):
        #     classifiedAlert = label
        #     # print(f"🚨 ALERT: {label} detected!")
        #     break
        if label in DANGEROUS_CLASSES:
            classifiedAlert = label
            break


def audio_callback(indata, frames, time, status):
    audio_buffer.extend(indata[:, 0])
    if len(audio_buffer) >= 44100 * BUFFER_DURATION:
        data = np.array(audio_buffer)
        process_audio_with_yamnet(data.copy(), 44100)
        audio_buffer.clear()

def main():
    print("Starting real-time audio classification...")
    with sd.InputStream(callback=audio_callback, channels=1, samplerate=44100):
        while True:
            sd.sleep(1000)

if __name__ == "__main__":
    main()