# PyoMyo
Python module for the Thalmic Labs Myo armband. 

Cross platform and multithreaded and works without the Myo SDK. 

```
pip install pyomyo
```
Documentation is in the Wiki, see [Getting Started](https://github.com/PerlinWarp/pyomyo/wiki/Getting-started).

![Playing breakout with sEMG](https://github.com/PerlinWarp/Neuro-Breakout/blob/main/media/Breakout.gif?raw=true "Breakout")

### PyoMyo Documentation
[Home](https://github.com/PerlinWarp/pyomyo/wiki)  
[Getting started](https://github.com/PerlinWarp/pyomyo/wiki/Getting-started)  
[Common Problems](https://github.com/PerlinWarp/pyomyo/wiki/Common-Problems)  
[Myo Placement](https://github.com/PerlinWarp/pyomyo/wiki/Myo-Placement)  

#### The big picture
[Why should you care?](https://github.com/PerlinWarp/pyomyo/wiki/Why-should-you-care%3F)  
[Basics of EMG Design](https://github.com/PerlinWarp/pyomyo/wiki/The-basics-of-EMG-design)  

[Links to other resources](https://github.com/PerlinWarp/pyomyo/wiki/Links)  

## Python Open-source Myo library

This library was made from a fork of the MIT licensed [dhzu/myo-raw.](https://github.com/dzhu/myo-raw)
Bug fixes from [Alvipe/myo-raw](https://github.com/Alvipe/myo-raw) were also added to stop crashes and also add essential features.  

This code was then updated to Python3, multithreading support was added then more bug fixes and other features were added, including support for all 3 EMG modes the Myo can use.  

**Note that sEMG data, the same kind gathered by the Myo is thought to be uniquely identifiable. Do not share this data without careful consideration of the future implications.**

Also note, the Myo is outdated hardware, over the last year I have noticed a steady incline in the cost of second hand Myos. Both of my Myo's were bought for under £100, I do not recommend spending more than that to acquire one. Instead of buying one you should [join the discord](https://discord.com/invite/mG58PVyk83) to create an open hardware alternative!

## Included Example Code
The examples sub-folder contains some different ways of using the pyomyo library. 
```
git clone https://github.com/PerlinWarp/pyomyo
```


### plot_emgs_mat.py
<p align="center">
<img src="https://i.imgur.com/SDa9baf.gif" alt="Left to Right Wrist movements."/>
</p>

Starts the Myo in mode 0x01 which provides data that's already preprocessed (bandpass filter + rectified).  
This data is then plotted in Matplotlib and is a good first step to see how the Myo works.  
Sliding your finger under each sensor on the Myo will help identify which plot is for sensor.

### dino_jump.py
<p align="center">
<img src="https://media3.giphy.com/media/7QPdXL6TRtA5Juvmnx/giphy.gif?cid=790b76118f3473e257d1da6173f7fe1fe114526dad4e0718&rid=giphy.gif&ct=g" alt="Chrome Dinosaur Game"/>
</p>

An example showing how to use the live classifier built into pyomyo, see [Getting Started](https://github.com/PerlinWarp/pyomyo/wiki/Getting-started) for more info.

### myo_multithreading_examp.py
Devs start here.  
This file shows how to use the library and get Myo data in a seperate thread.


## Myo Modes Explained
To communicate with the Myo, I used [dzhu's myo-raw](https://github.com/dzhu/myo-raw).
Then added some functions from [Alvipe](https://github.com/dzhu/myo-raw/pull/23) to allow changing of the Myo's LED.

emg_mode.PREPROCESSED (0x01)  
By default myo-raw sends 50Hz data that has been rectified and filtered, using a hidden 0x01 mode.  

emg_mode.FILTERED (0x02)  
Alvipe added the ability to also get filtered non-rectified sEMG (thanks Alvipe).  

emg_mode.RAW (0x03)   
Then I further added the ability to get true raw non-filtered data at 200Hz.
This data is unrectified but scales from -128 and 127.  

Sample data and a comparison between data captured in these modes can be found in [MyoEMGPreprocessing.ipynb](https://github.com/PerlinWarp/Neuro-Breakout/blob/main/Notebooks/MyoModesCompared/MyoEMGPreprocessing.ipynb)

## The library  

### pyomyo.py
Prints sEMG readings at 200Hz straight from the Myo's ADC using the raw EMG mode.   
Each EMG readings is between -128 and 127, it is the most "raw" the Myo can provide, however it's unlikely to be useful without extra processing.
This file is also where the Myo driver is implemented, which uses Serial commands which are then sent over Bluetooth to interact with the Myo.

### Classifier.py
Implements a live classifier using the k-nearest neighbors algorithm.  
Press a number from 0-9 to label incoming data as the class represented by the number.  
Press e to delete all the data you have gathered.  
Once two classes have been made new data is automatically classified. Labelled data is stored as a numpy array in the ``data\`` directory.
