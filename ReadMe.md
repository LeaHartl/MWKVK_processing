# Code to process MWK and VK data files (glacier and meteo data)  

This repo is related to glaciological and meteorological data from Mullwitzkees (MWK) and Venedigerkees (VK), two glaciers in the Hohe Tauern range of the Austrian Alps. New data is being added to existing publication series on the PANGAEA data platform and an accompanying publication has been submitted to Earth System Science Data (Copernicus publications).

The scripts require the folowing directories to be present in the same directory as the .py files: "out", "figs", "AWS". Additional file paths to input data need to be set in the scripts, see comments therein.

## GLACIER data:      
**ProcessExcl.py:**  
+ Reads point mass balance stake data in excel files for VK and MWK (supplied by Bernd Seiser & Martin Stocker-Waldhuber for Vk and MWK, respectively).    
+ Calls **Uncertainty.py** for uncertainty computation of point data followig approach described in Geibel et al (2022)  
+ writes formatted csv files of point MB data for each glacier (annual, intermediate, inter_cumulative).   

**ProcessShapefiles.py**
+ reads shapefiles of glacierwide massbalance (polygons of iso-areas) and probe data (point shapefiles) provided by BS and MS (as above)
+ writes probe data to formated tabular file  
+ generates figures for winter and annual mass balance showing iso-areas as maps in subplots for each year of the timeseries. Four figures in total, two for each glacier (figs 7 - 10, saved to directory "figs")


**GlacierData_Plots1.py:**   
+ loads files of point mb data produced in previous scripts
+ plots related figures (figs 1 - 6, saved to directory "figs")

**GlacierData_Plots2.py:**  
+ reads and plots data as downloaded from pangaea (note: minor changes to the data files to fix typos/errors)  
+ MWK data: https://doi.pangaea.de/10.1594/PANGAEA.806662 (Stocker-Waldhuber et al. (2016). For bulk download, use option "Download ZIP file containing all datasets as tab-delimited text")  
+ VK data: https://doi.pangaea.de/10.1594/PANGAEA.833232 (Seiser and Fischer (2016). For bulk download, use option "Download ZIP file containing all datasets as tab-delimited text")
+ makes figure for cumulative MB (glacier wider summer, winter, annual) for both glaciers (fig 11)
+ makes figure with subplots for each year showing MB parameters and ELA in elevations zones (horizontal bar plots, fig 12)



## METEO: 
Code to load the data files as downloaded from pangaea:				
**AWS_pangaeadata.py**       
+ loops through the folder with the .tab files    
+ loops through each file to remove the header     
+ loads and merges the data for all years 			
+ passes the data to the plotting functions in **AWS_plots_helpers.py**   


Code used to do the initial formating and QC of the AWS data from AWS_VK and AWS_MWK (weather stations Keeskogel Südgrat and Defreggerhaus)    
**AWS_processing.py**  
+ loads data files, concatenates if needed (data loaded from directory "AWS")
+ applies quality flags 
+ saves csv of raw data and csv of processed data with quality flags in cosistent formatting (files saved to directory "AWS")
**AWS_graphics.py**   
+ Imports **AWS_plots_helpers.py** for plotting functions 
+ produces times series figures (saved to directory "figs") of meteo parameters, wind rose plot, snow depth plot (unfiltered vs. filtered) 
+ produces some statistics for the meteo data, saved as tables to directory "out"



# References 
Geibel, L., Huss, M., Kurzböck, C., Hodel, E., Bauder, A., and Farinotti, D. (2022) Rescue and homogenization of 140 years of glacier mass balance data in Switzerland, Earth System Science Data, 14, 3293–3312.     
https://essd.copernicus.org/articles/14/3293/2022/essd-14-3293-2022.html    



Seiser, B., Fischer, A. (2016): Glacier mass balances and elevation zones of Venedigerkees, Hohe Tauern, Austria, 2011/2012 et seq. Institut für Interdisziplinäre Gebirgsforschung der Österreichischen Akademie der Wissenschaften, Innsbruck, PANGAEA, https://doi.org/10.1594/PANGAEA.833232   



Stocker-Waldhuber, M., Fischer, A., Kuhn, M. (2016): Glacier mass balances and elevation zones of Mullwitzkees, Hohe Tauern, Austria, 2006/2007 et seq. Institut für Interdisziplinäre Gebirgsforschung der Österreichischen Akademie der Wissenschaften, Innsbruck, PANGAEA, https://doi.org/10.1594/PANGAEA.806662   

