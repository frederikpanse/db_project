# Are You Still Booking Train Tickets Under the Assumption of No Delays?

<p align="center">
  <img src="doc/fig/maps_KI_01_all_data_cmap.png" height="400">
</p>

This repo contains the code used for a project to find the most reliable train route going from Stuttgart to Frankfurt (Main) as part of the lecture *Data Literacy* at the University of Tuebingen.

---

The optimized route has less than half the delay of the fastest proposed route by Deutsche Bahn. The most important factors contributing to the delay of a given station are the distance of the station to the border and the (relative) number of train rides at the station.

<p align="center">
  <img src="doc/fig/maps_KI_03_reliable_vs_fastest_zoomed_Carto.png" height="300">
  <img src="doc/fig/plot_JH_01_feature_importance.png" height="300">
</p>

Trains are a more delayed on weekdays than on weekends. However, the optimal route is the most reliable no matter when you travel.

<p align="center">
  <img src="doc/fig/plot_FP_03_WeekdayWeekend.jpeg" height="250">
</p>

## Structure

You will find the data we used in the directory `.\dat`, the experiments we conducted in `.\exp`, and the report and (even more) figures in `.\doc`.
