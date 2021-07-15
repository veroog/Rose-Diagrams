#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul  6 20:20:54 2021
Sources: https://stackoverflow.com/questions/55854988/subplots-onto-a-basemap
        https://windrose.readthedocs.io/en/latest/usage.html
@author: Veronica Guzman
"""

#### ***** PLOT AZIMUTH LINES ON MAP ***** ####
   ## example uses West Texas
import numpy as np
import math
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import pandas as pd
from obspy.clients.fdsn import Client
import shapefile as shp 
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import matplotlib

### Obspy inputs
client = Client("IRIS") # IRIS DMC
network='TX'
### Stations to be plotted 
stations = ['PB11', 'PB33', 'PB05', 'PB09'] 

### Extend of map
minlat=30.5
maxlat=32.1
minlon=-105
maxlon=-102.7

### Generate figure
fig, ax = plt.subplots(figsize=(20,15))

### Create basemap
m = Basemap(llcrnrlon=minlon,llcrnrlat=maxlat,urcrnrlon=maxlon,urcrnrlat=minlat,\
            rsphere=(6378137.00,6356752.3142),\
            resolution='l',\
            lat_0=40.,lon_0=-20.,lat_ts=20, ax=ax, epsg=4203)
m.drawcountries()
m.fillcontinents(color='wheat', lake_color='skyblue')
m.fillcontinents(color='tan',lake_color='lightblue')
m.drawmapboundary(fill_color='lightblue')
m.drawstates(linewidth=1, linestyle='solid', color='black')
m.drawparallels(np.arange(29,34.5,0.5),labels=[1,0,1,1])  ## change as preferred 
m.drawmeridians(np.arange(-104.5,-99,0.5),labels=[1,1,1,0])  ## change as preferred 

### Attach figure to basemap
#fig.bmap = m ### dont really need this. 

### Invert the y-axis
ax.yaxis.set_inverted(False)

### Add extras (TX shapefile, TX counties, etc.) ### Need shapefiles. These are easily downloadable 
sf = shp.Reader("/Tx_CntyBndry_Jurisdictional_TIGER/Tx_CntyBndry_Jurisdictional_TIGER.shp")
for shape in sf.shapeRecords():
    x2 = [i[0] for i in shape.shape.points[:]]
    y2 = [i[1] for i in shape.shape.points[:]]
    plt.plot(x2,y2, color = 'dimgrey')

### Add North arrow
x, y, arrow_length = 0.05, 0.95, 0.1
ax.annotate('N', xy=(x, y), xytext=(x, y-arrow_length),
            arrowprops=dict(facecolor='black', width=5, headwidth=15),
            ha='center', va='center', fontsize=20,
            xycoords=ax.transAxes)
hfont = {'fontname':'Helvetica'}

### Function to plot rose diagram on map 
def generate_rose(mapx, mapy, ax, width, xvals, yvals, station):
    ax_h = inset_axes(ax, width=0.9, \
                    height=0.9, \
                    loc='center', \
                    bbox_to_anchor=(mapx, mapy), \
                    bbox_transform=ax.transData, \
                   # borderpad=0, \
                    #axes_kwargs={'alpha': 0.35, 'visible': True}, \
                    axes_class=matplotlib.projections.get_projection_class('polar'))
    ax_h.bar(xvals, y,width,  edgecolor='green')
    ax_h.set_theta_zero_location('N')
    ax_h.set_theta_direction(-1)
    ax_h.grid(True)
    ax_h.set_title(station, fontsize=8, **hfont)
    ax_h.set_rgrids(np.arange(1, half.max() + 1, 2), angle=0, weight= 'black', fontsize=5)
    ax_h.axes.xaxis.set_ticklabels([]) #remove tick labels in polar coordinates. 
    return ax_h

### Plot rose diagram on map 
 # loop through every station
for i in stations:
    ## ** If you already have spreadsheets with SWS results, use following lines: ** ## 
       ##  one spreadsheet per station ## 
    
    #df = pd.read_excel('SWS_Results/SWS_Splitting_Results_Station_' + i + '.xlsx', index_col=0, header=None)
    #events_latitudes = df.iloc[:, 5] ## specifc column for SWS resutls - Outputed from % Regan Robinson Script
    #events_longitudes = df.iloc[:, 6] ## specifc column for SWS resutls - Outputed from % Regan Robinson Script
    #phi = df.iloc[:, 14] ## specifc column for SWS resutls - Outputed from % Regan Robinson Script
    #phi.reset_index()
    
    ## Let's create dummy datapoints with Lat/Long and SWS angles. 
    size = 20 
    df = pd.DataFrame(columns=['events_latitudes', 'events_longitudes', 'phi'])
    df['events_latitudes']= np.random.uniform(minlat,maxlat, size = size) #creates lat within our study area.
    df['events_longitudes']= np.random.uniform(minlon, maxlon, size = size) #creates long  within our study area.
    df['phi'] = np.random.uniform(0,360, size = size)
    phi = df['phi']
    phi.reset_index()
    
    ### Get station coordinates from Obspy
    sta1 = client.get_stations(network=network, station=i, level="channel",channel='HH*')
    net = sta1[0]
    sta = net[0]
    # print(sta.code)
    # print(sta.latitude) 
    # print(sta.longitude)
    
    angles, bins = np.histogram(phi, bins = np.arange(-5, 366,5))   
    half = np.sum(np.split(angles, 2), 0)  
    half = np.concatenate([half, half]) 
    
    xvals = np.deg2rad(np.arange(0,370, 5))
    y = half
    width=np.deg2rad(5)
    bax = generate_rose(sta.longitude, sta.latitude, ax, width, xvals,y, i)

plt.savefig('RoseDiagram_Test.png', bbox_inches="tight")
