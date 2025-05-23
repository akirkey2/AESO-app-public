# AESO-app-public
Dash app for AESO generation data viz and analysis

Link to dash: https://aeso-app-public.onrender.com (first load takes a couple of minutes due to host service unfreezing).

Thanks for checking out my dash app! Raw data files are available in /assets but in order to host the dash for free I've adapted my code to make a condensed dataset called "mini_df.csv" from which all visualization are made. 

Updates are constantly being rolled out and if you have questions, comments or suggestions, please contact me at: akirkey2@gmail.com!

Data sources: 

Generation: https://aeso.app.box.com/s/qofgn9axnnw6uq3ip1goiq2ngb11txe5/folder/196178549071
Price Data: https://public.tableau.com/app/profile/market.analytics/viz/AnnualStatistics_16161854228350/Introduction
Emissions Factors: https://www.nrel.gov/docs/fy21osti/80580.pdf
Weather Data: Accessed using this bash command from terminal (location:pincher creek, AB): for year in `seq 2023 2025`;do for month in `seq 1 12`;do wget --content-disposition "https://climate.weather.gc.ca/climate_data/bulk_data_e.html?format=csv&stationID=27218&Year=${year}&Month=${month}&Day=14&timeframe=1&submit= Download+Data" ;done;done
