import random 
import shutil

filenames= [f"{x:05d}"+".jpg" for x in random.sample(range(500, 1800), 30)]
src , target = './nuclie00/', './sample_train/nuclie00/'

for file in filenames:
    shutil.copyfile(src+file, target+file)
