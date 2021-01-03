# Analyze GPX tracks

I got a little worried that Polar GritX doesn't show very correctly maximum speed in downhill skiing (among other sports) and looked at that more in detail. Here is a small piece of code to self-analyze gpx tracks and example gpx file.

Polar GritX gave max speed of 75.7 km/h for the run below. Speed has now been computed from the 3D x(t) curve with three different integration times without any filtering, fitting or model.

![Image](https://github.com/stenvala/gpx-analyzer/blob/master/data/fastest.png?raw=true)
