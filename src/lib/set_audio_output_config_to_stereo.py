import subprocess

# Set the sample rate to 24000 Hz
sample_rate = 24000

# Start the recording process
subprocess.run(["arecord", "-r", str(sample_rate), "-f", "S32_LE", "-D", "hw:sndrpigooglevoi,0", "-c", "2", "-d", "5", "-i", "plug:mic"], stdout=subprocess.PIPE)

# Get the recorded audio data
audio_data = subprocess.check_output(["arecord", "-r", str(sample_rate), "-f", "S32_LE", "-D", "hw:sndrpigooglevoi,0", "-c", "2", "-d", "5", "-i", "plug:mic"], stderr=subprocess.PIPE)

# Stop the recording process
subprocess.run(["arecord", "-r", str(sample_rate), "-f", "S32_LE", "-D", "hw:sndrpigooglevoi,0", "-c", "2", "-d", "5", "-i", "plug:mic"], stderr=subprocess.PIPE)

# Save the recorded audio data to a file
with open("test.wav", "wb") as f:
    f.write(audio_data)
