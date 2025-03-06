NetTracer3D is a python package developed for both 2D and 3D analysis of microscopic images in the .tif file format. It supports generation of 3D networks showing the relationships between objects (or nodes) in three dimensional space, either based on their own proximity or connectivity via connecting objects such as nerves or blood vessels. In addition to these functionalities are several advanced 3D data processing algorithms, such as labeling of branched structures or abstraction of branched structures into networks. Note that nettracer3d uses segmented data, which can be segmented from other softwares such as ImageJ and imported into NetTracer3D, although it does offer its own segmentation via intensity and volumetric thresholding, or random forest machine learning segmentation. NetTracer3D currently has a fully functional GUI. To use the GUI, after installing the nettracer3d package via pip, enter the command 'nettracer3d' in your command prompt:


This gui is built from the PyQt6 package and therefore may not function on dockers or virtual envs that are unable to support PyQt6 displays. More advanced documentation is coming down the line, but for now please see: https://www.youtube.com/watch?v=cRatn5VTWDY
for a video tutorial on using the GUI.

NetTracer3D is free to use/fork for academic/nonprofit use so long as citation is provided, and is available for commercial use at a fee (see license file for information).

NetTracer3D was developed by Liam McLaughlin while working under Dr. Sanjay Jain at Washington University School of Medicine.

-- Version 0.6.1 updates --

1. New feature for the machine learning segmenter. Now has a RAM lock mode which will always limit it to computing 1 chunk at a time, in both the interactive segmenter and the gross-segmenter. Feature map calculation within the chunk is made parallel to compensate which should allow this to function more optimally with RAM without really sacrificing performance. This should prevent the segmenter from majorly leaking memory in large arrays.
2. New function - 'Image' -> 'Select Objects'. Essentially just arbitrary selects/deselects lists of nodes or edges from the user in case there are some they are interested in but can't conveniently find. Allows imports from spreadsheets in case the user preorganizes some set of objects they want to select/deselect.
3. Brightness/Contrast now shades out of 65,535 instead of 255 which should allow better brightening options to images above 8bit depth.
4. Select all function updated to use the mini highlight overlay in larger images. Also reports the number of nodes/edges in the array in the cmd window when used.
5. Deleted the now unused 'hub_getter.py' script from the package.