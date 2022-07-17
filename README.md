# FIBSEM_segmentation
Deep learning and image processing scripts for Segmenting the FIBSEM data. For more details about the ongoing research follow this [link](https://github.com/nirajmg/FIBSEM_segmentation/blob/main/FIB_SEM_Segmentation.pdf). 

The scripts are built on pymsdtorch library. For more details on how to use this library refer the documentation [here](https://pymsdtorch.readthedocs.io/en/latest/).

## Files
**split_nuclie.py** is the script used for pre processing ROI1, ROI2 and ROI3 and splitting the stack into single nuclie.The documentation for the image processing features of opencv2, which this script uses, may be found [here](https://docs.opencv.org/3.4/d2/d96/tutorial_py_table_of_contents_imgproc.html). 

**parse_save_4labels** notebook is used to further process the annotated data and add additional labels to the masks. This generates tiff files of the data for training the network.  

**train_and_segment** notebook is used to train  msdnets and Unets on the generated data from the pre processing scripts. 

**load_model_with_100_batch** notebook is used for segmenting the data in batches using the trained networks. This generates the jpeg files for every label. The batch size can be reduced for smaller systems. 

**CleanImages_GenerateMovie** is a post processing notebook which can be used to clean up the images and also to generate a movie of the 3d structures.





