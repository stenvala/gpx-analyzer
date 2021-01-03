import gpxpy
import gpxpy.gpx
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


def parse_gpx(filename):
    distances = [0]
    speeds = [0]
    times = [0]
    with open(filename, 'r') as gpx_file:
        gpx = gpxpy.parse(gpx_file)
        for track in gpx.tracks:
            for segment in track.segments:
                for (point_no, point) in enumerate(segment.points):
                    if point_no > 0:
                        p2 = segment.points[point_no - 1]
                        speed = point.speed_between(p2) * 3.6
                        # Difference is always 1 or 0.999 s unless there is pause
                        # Pausing is not computable in csv data, so use here 1 to be able to match times
                        diff_t = 1  # point.time_difference(p2)
                        diff_3d = point.distance_3d(p2)
                        speeds.append(speed)
                        times.append(diff_t + times[-1])
                        distances.append(diff_3d + distances[-1])
    return times, distances, speeds


def moving_average(numbers, window_size):
    numbers_series = pd.Series(numbers)
    windows = numbers_series.rolling(window_size)
    moving_averages = windows.mean()
    return moving_averages.tolist()


def get_max_speed(numbers, window_size):
    return max(moving_average(numbers, window_size)[window_size - 1:])


def time_to_sec(t):
    parts = t.split(':')
    return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])


def fix_csv_gaps(csv):
    speeds = [0]
    times = [0]
    for i in csv.Speed:
        if np.isnan(i):
            continue
        speeds.append(i)
        times.append(times[-1] + 1)
    return times, speeds


csv = pd.read_csv('data/2020-12-31-DownHillSki.csv', usecols=['Time', 'Speed'])
csv.Time = csv.Time.apply(time_to_sec)
csv_times, csv_speeds = fix_csv_gaps(csv)

#  compute data
times, distances, speeds = parse_gpx('data/2020-12-31-DownHillSki.gpx')

"""
for k in range(1, 121):
    max_speed = get_max_speed(speeds, k)
    print('Max speed over %s s is %s km/h' % (k, max_speed))
"""

tmin = 24320  # 28160
tmin = 22320
tmin = 25850
t_diff = 160
tmax = tmin + t_diff

min_ind = next(x[0] for x in enumerate(times) if x[1] > tmin)
max_ind = next(x[0] for x in enumerate(times) if x[1] > tmax) - 1

fig, ax1 = plt.subplots()

time_scale = [x-times[min_ind] for x in times]
print(len(time_scale))
print(len(csv_times))
print(len(csv.Time))
# There is this kind of strange 25 s difference at higher times in csv data. May be related to satellite locking.
polar_shift = -25
polar_t = [x-times[min_ind]+polar_shift for x in csv_times]
max_polar_speed = max([x[1] for x in enumerate(
    csv_speeds) if polar_t[x[0]] > 0 and polar_t[x[0]] < t_diff])

for k in [1, 5, 10]:
    max_speed_graph = moving_average(speeds, k)
    max_speed = get_max_speed(speeds[min_ind:max_ind], k)
    ax1.plot(time_scale, max_speed_graph, label="Int = %s s (%s km/h)" %
             (k, round(max_speed, 2)), marker=".", markersize=5)

ax1.plot(polar_t, csv_speeds, color="black",
         label="Polar GritX (%s km/h)" % max_polar_speed)

ax1.set_xlabel('Time [s]')
ax1.set_ylabel('Speed [km/h]')

ax2 = ax1.twinx()

ax1.set_xlim(0, tmax-tmin)
ax1.set_ylim(0, 100)

dist = [x-distances[min_ind] for x in distances]
ax2.plot(time_scale, dist, color='black', ls='dashed')

ax2.set_ylabel('Distance [m]')
# ax2.set_ylim(0, dist[max_ind])
ax2.set_ylim(0, 1600)

fig.tight_layout()  # otherwise the right y-label is slightly clipped

ax1.legend(loc=2, frameon=False)
plt.show()
