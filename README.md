# Data-Vis-for-YouTube-Channels
Web Scraping with Selenium | Data Visualization with Seaborn | Web UI with FastApi

How to use : 
1) Get data from any youtube channel using http://127.0.0.1:8000/selenium/{ChannelName}
    
	example : 
		
				(youtube.com/c/lordpac)
				http://127.0.0.1:8000/selenium/lordpac
			
2) Wait until all data loads and see the list of results.
3) use http://127.0.0.1:8000/plot/{PlotName} to scatter plots
    
	example :
	
				http://127.0.0.1:8000/plot/view-duration
   				http://127.0.0.1:8000/plot/view-titlelength
