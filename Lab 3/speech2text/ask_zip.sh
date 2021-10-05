echo \"What is your zipcode?\" | festival --tts
arecord -D hw:2,0 -f cd -c1 -r 48000 -d 5 -t wav ask_zip.wav
python3 ask_zipcode.py ask_zip.wav

