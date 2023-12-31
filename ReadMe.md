# Code to process MWK and VK data files (glacier and meteo data)


## GLACIER data:      
**ProcessExcl.py:**  
+ Reads point mass balance stake data in excel files for VK and MWK (supplie by Bernd Seiser & Martin Stocker-Waldhuber, who coordinate the field work).    
+ Calls **Uncertainty.py** for uncertainty computation of point data.    
+ writes formatted files (annual, intermediate, inter_cumulative).   

**ProcessShapefiles.py**
+ reads shapefiles of glacierwide massbalance (polygons of isoareas) and probe data (point shapefiles) provided by BS and MS (as above)
+ writes probe data to formated tabular file  
+ generates figures for winter and annual mass balance showing iso-areas as maps in subplots for each year of the timeseries. Four figures in total, two for each glacier (figs 7 - 10)


**GlacierData_Plots1.py:**   
+ loads files of point mb data produced in previous scripts
+ plots related figures for ESSD paper (figs 1 - 6)

**GlacierData_Plots2.py:**  
+ reads and plots data as downloaded from pangaea (note: minor changes to the data files to fix typos/errors)
+ makes figure for cumulative MB (glacier wider summer, winter, annual) for both glaciers (fig 11)
+ makes figure with subplots for each year showing MB parameters and ELA in elevations zones (horizontal bar plots, fig 12)



## METEO: 
Format and plot AWS data from AWS_VK and AWS_MWK (stations Keeskogel Südgrat and Defreggerhaus)    
**AWS_processing.py**  
+ loads data files, concatenates if needed (data loaded directory "AWS")
+ applies quality flags 
+ saves csv of raw data and csv of processed data with quality flags in cosistent formatting (files saved to directory "AWS")
**AWS_graphics.py**   
+ Imports **AWS_plots_helpers.py** for plotting functions 
+ produces times series figures (saved to directory "figs") of meteo parameters, wind rose plot, snow depth plot (unfiltered vs. filtered) 
+ produces some statistics for the meteo data, saved as tables to directory "out"






