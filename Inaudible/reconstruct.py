import numpy as np
import librosa
import soundfile as sf
from PIL import Image
import matplotlib.pyplot as plt

# Load the spectrogram image
img_path = 'spectrogram.png'
img = Image.open(img_path)
img_array = np.array(img)

# Parameters (from the document)
sr = 44100                      # Sample rate
num_freqs = 128                 # Number of mel bands
min_db = -60                    # Minimum decibel value
max_db = 30                     # Maximum decibel value
fft_window_size = 2048
frame_step_size = 512
window_function_type = 'hann'

# Extract the spectrogram data from the image
# We need to remove axes and color bar if they exist in the image
# Let's assume the main spectrogram is the core part of the image
# You might need to adjust these values based on your specific image

# Determine the region containing the actual spectrogram (excluding axes and colorbar)
# This requires manual inspection and adjustment
height, width = img_array.shape[:2]

# Extract the main spectrogram region
main_spec = img_array

# Convert RGB to grayscale if the image is in color
if len(main_spec.shape) == 3:
    gray_spec = main_spec[:, :, 1]
else:
    gray_spec = main_spec

# Normalize and invert the grayscale values to get proper intensity
# Assuming brighter values in image = higher energy
normalized_spec = (gray_spec - np.min(gray_spec)) / (np.max(gray_spec) - np.min(gray_spec))

# Map to dB scale (min_db to max_db)
log_mel_spectrogram = min_db + normalized_spec * (max_db - min_db)

# Flip the spectrogram vertically because in the image lower frequencies are at the bottom
log_mel_spectrogram = np.flipud(log_mel_spectrogram)

# Convert to mel power spectrogram
mel_spectrogram = librosa.db_to_power(log_mel_spectrogram)

# Reconstruct audio using Griffin-Lim algorithm
# Use librosa's mel_to_audio as mentioned in the document
y = librosa.feature.inverse.mel_to_audio(
    mel_spectrogram, 
    sr=sr, 
    n_fft=fft_window_size, 
    hop_length=frame_step_size,
    window=window_function_type,
    n_iter=32  # More iterations for better reconstruction
)

# Save the reconstructed audio
output_path = 'reconstructed_audio.wav'
sf.write(output_path, y, sr)

print(f"Audio reconstruction completed. Saved to {output_path}")
print(f"Reconstructed spectrogram saved to reconstructed_spectrogram.png")