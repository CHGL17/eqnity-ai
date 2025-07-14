import os
import soundfile as sf

path = "C:\\Users\\root\\Documents\\REAPER Media\\Media\\temp_audio\\tmphaw6hzgb.wav\\test-ai.wav"
print(os.path.getsize(path))

with open(path, "rb") as f:
    f.read(1)

audio, sr = sf.read(path)

print("File read successfully.", audio, sr)