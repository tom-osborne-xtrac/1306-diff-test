# XT-13944 - P1306 Loaded Rig EoL
# Diff Test Analysis
# Author: Tom Osborne
# Version: v1.0
# Date: 03 November 2021

import tkinter as tk
from tkinter import filedialog
import matplotlib.pyplot as plt
from matplotlib import collections as matcoll
import os
import pandas as pd
import csv
import numpy as np
from scipy.ndimage.filters import uniform_filter1d


# -------------------------------------------------------------------------------------- #
def smooth(x, window_len, window='hanning'):
    """smooth the data using a window with requested size.

    This method is based on the convolution of a scaled window with the signal.
    The signal is prepared by introducing reflected copies of the signal
    (with the window size) in both ends so that transient parts are minimized
    in the beginning and end part of the output signal.

    input:
        x: the input signal
        window_len: the dimension of the smoothing window; should be an odd integer
        window: the type of window from 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'
            flat window will produce a moving average smoothing.

    output:
        the smoothed signal
    Source: SciPy Cookbook -  https://scipy-cookbook.readthedocs.io/items/SignalSmooth.html
    """

    if x.ndim != 1:
        raise ValueError("smooth only accepts 1 dimension arrays.")

    if x.size < window_len:
        raise ValueError("Input vector needs to be bigger than window size.")

    if window_len < 3:
        return x

    if window not in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
        raise ValueError("Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'")

    s = np.r_[x[window_len:0:-1], x, x[-2:-window_len:-1]]
    # print(len(s))
    if window == 'flat':  # moving average
        w = np.ones(window_len, 'd')
    else:
        w = eval('np.' + window + '(window_len)')

    y = np.convolve(w / w.sum(), s, mode='valid')
    return y[int((window_len/2-1)):-int((window_len/2)+1)]
# -------------------------------------------------------------------------------------- #
# -------------------------------------------------------------------------------------- #


# Define filePath
# ---------------------- #
root = tk.Tk()
root.withdraw()
filePath = filedialog.askopenfilename()
fileName = os.path.basename(filePath)

print("Location:", filePath)
print("File: ", fileName)

# Parse Data
# ---------------------- #
row_count = 0
header_row = 4  # 5th row
Headers = []

# Data Channels
data_TimeIntoTest = []      # Time Into test [s]
data_EventTime = []         # Event Time [s]
data_OPSpeed1 = []          # OP Speed 1 [rpm]
data_OPTorque1 = []         # OP Torque 1 [Nm]
data_OPSpeed2 = []          # OP Speed 2 [rpm]
data_OPTorque2 = []         # OP Torque 2 [Nm]
data_AvgTotalOPTrq = []     # Avg Total Output Torque [Nm]
data_IPSpeed1 = []          # IP Speed 1 [rpm]
data_IPTorque1 = []         # IP Torque 1 [Nm]
data_ActualGearNo = []      # Actual gear number [#]

# Attempt to do the above but with pandas dataframe
data_df = pd.read_csv(filePath, sep=",", header=3)
# print(data_df['Event Time'])

gear_ratios = {
    1: 12.803,
    2: 9.267,
    3: 7.058,
    4: 5.581,
    5: 4.562,
    6: 3.878,
    7: 3.435
}

with open(filePath, 'r') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')

    for row in csv_reader:
        if row_count == 0:
            TestName = row
            print(TestName)
        elif row_count == 1:
            TestDate = row
            print(TestDate)
        elif row_count == 2:
            TestTime = row
            print(TestTime)
        elif row_count == 4:
            Headers.append(row)
            print(Headers)
        elif row_count > 5:
            data_TimeIntoTest.append(float(row[0]))    # Time Into Test [s]
            data_EventTime.append(float(row[1]))       # Event Time [s]
            data_OPSpeed1.append(float(row[2]))        # OP Speed 1 [rpm]
            data_OPTorque1.append(float(row[3]))       # OP Torque 1 [Nm]
            data_OPSpeed2.append(float(row[4]))        # OP Speed 2 [rpm]
            data_OPTorque2.append(float(row[5]))       # OP Torque 2 [rpm]
            data_AvgTotalOPTrq.append(float(row[6]))   # Avg Total Output Torque [Nm]
            data_IPSpeed1.append(float(row[7]))        # IP Speed 1 [rpm]
            data_IPTorque1.append(float(row[8]))       # IP Torque 1 [Nm]
            data_ActualGearNo.append(row[9])           # Actual gear number [#]
        row_count += 1


# Calculated Channels
# ---------------------- #
# Sample Rate
sample_rates = []
for i in range(1, len(data_EventTime)):
    calc = data_EventTime[i] - data_EventTime[i-1]
    sample_rates.append(calc)
sample_rate = int(1 / (sum(sample_rates) / len(sample_rates)))
print("Sample rate:", sample_rate, "Hz")

# Gear used
count_Gears = {i: data_ActualGearNo.count(i) for i in data_ActualGearNo if i != ""}
actualGear = [int(k) for k, v in count_Gears.items() if v == max(count_Gears.values())]
gears_hr = {
    1: "1st",
    2: "2nd",
    3: "3rd",
    4: "4th",
    5: "5th",
    6: "6th",
    7: "7th"
}
actualGear_hr = gears_hr[actualGear[0]]
print("Gears:", count_Gears, actualGear, actualGear_hr)


# Input torque gradient, used for detecting ramp sections
calc_IPTrqGradient = np.gradient(uniform_filter1d(data_IPTorque1, size=int(sample_rate)), edge_order=2) * 10
calc_IPTrqGradient_smoothed = smooth(calc_IPTrqGradient, sample_rate+1)

# Axle torque (x-axis on diff graph)
calc_AxleTrqFromInput = []

# Lookup for the actual gear
gear_ratio = gear_ratios[actualGear[0]]
for i in range(len(data_IPTorque1)):
    calc = data_IPTorque1[i] * gear_ratio
    calc_AxleTrqFromInput.append(calc)

calc_AxleTrqFromOutput = []
for i in range(len(data_OPTorque1)):
    calc = data_OPTorque1[i] + data_OPTorque2[i]
    calc_AxleTrqFromOutput.append(calc)

# Difference between Axle Torque calculation methods
calc_AxleTrqDifference = []
calc_AxleTrqDifference_IP = []
for i in range(len(calc_AxleTrqFromOutput)):
    calc = calc_AxleTrqFromInput[i] - calc_AxleTrqFromOutput[i]
    calc_AxleTrqDifference.append(calc)

    calc2 = (calc_AxleTrqFromInput[i] - calc_AxleTrqFromOutput[i]) / gear_ratio
    calc_AxleTrqDifference_IP.append(calc2)

# Locking torque (y-axis on diff graph)
calc_LockTrq = []
for i in range(len(data_OPTorque1)):
    calc = data_OPTorque1[i] - data_OPTorque2[i]
    calc_LockTrq.append(calc)

# Speed delta across diff
calc_OPSpeedDelta = []
calc_OPSpeedDelta_smoothed = []
for i in range(len(data_OPSpeed1)):
    calc = data_OPSpeed1[i] - data_OPSpeed2[i]
    calc_OPSpeedDelta.append(calc)
calc_OPSpeedDelta_smoothed = smooth(np.array(calc_OPSpeedDelta), sample_rate+1)

# Time elapsed
max_data_EventTime = max(data_EventTime)
print("Test Time Elapsed:", max_data_EventTime, "seconds")

# Set points for torque analysis graphs
set_points_x = [-800, -400, -200, -100, 0, 100, 200, 400, 800]
set_points = []
for i in range(len(set_points_x)):
    pair = [(set_points_x[i], 0), (set_points_x[i], 1000)]
    set_points.append(pair)
plot_set_points = matcoll.LineCollection(set_points)


# Filter data
# ---------------------- #
data_filtered_LockTrqL = []
data_filtered_LockTrqR = []
data_filtered_AxleTrqFromOP_L = []
data_filtered_AxleTrqFromIP_L = []
data_filtered_AxleTrqFromOP_R = []
data_filtered_AxleTrqFromIP_R = []
data_filtered_EventTimeL = []
data_filtered_EventTimeR = []
zero_count_L = 0
zero_count_R = 0

# Simplify code
# This section where the data is split into Left and Right lists could possibly be simplified.
# If we use a data structure where the data for left and right can be separated into different columns,
# rather than different lists all together, we might be able to reduce the repetition in the code

for i in range(len(data_EventTime)):
    # Add zero values
    if abs(calc_AxleTrqFromOutput[i]) < 50 and 0.5 > calc_IPTrqGradient[i] > -0.5:
        if calc_OPSpeedDelta[i] > 15 and zero_count_R < sample_rate * 1:
            data_filtered_AxleTrqFromOP_R.append(calc_AxleTrqFromOutput[i])
            data_filtered_AxleTrqFromIP_R.append(calc_AxleTrqFromInput[i])
            data_filtered_LockTrqR.append(abs(calc_LockTrq[i]))
            data_filtered_EventTimeR.append(data_EventTime[i])
            zero_count_R += 1
        elif calc_OPSpeedDelta[i] < -15 and zero_count_L < sample_rate * 1:
            data_filtered_AxleTrqFromOP_L.append(calc_AxleTrqFromOutput[i])
            data_filtered_AxleTrqFromIP_L.append(calc_AxleTrqFromInput[i])
            data_filtered_LockTrqL.append(abs(calc_LockTrq[i]))
            data_filtered_EventTimeL.append(data_EventTime[i])
            zero_count_L += 1
    # Add test point values
    elif abs(calc_AxleTrqFromOutput[i]) > 50:  # Filter out zero values
        if 0.5 > calc_IPTrqGradient[i] > -0.5:  # Filter out ramped sections
            if calc_OPSpeedDelta[i] > 0:  # Split into L & R series. L-R so +ve = RH Corner
                data_filtered_EventTimeR.append(data_EventTime[i])
                data_filtered_AxleTrqFromOP_R.append(calc_AxleTrqFromOutput[i])
                data_filtered_AxleTrqFromIP_R.append(calc_AxleTrqFromInput[i])
                data_filtered_LockTrqR.append(abs(calc_LockTrq[i]))
                # print("RH:", i, calc_AxleTrqFromOutput[i], calc_AxleTrqFromInput[i])
            else:
                data_filtered_EventTimeL.append(data_EventTime[i])
                data_filtered_AxleTrqFromOP_L.append(calc_AxleTrqFromOutput[i])
                data_filtered_AxleTrqFromIP_L.append(calc_AxleTrqFromInput[i])
                data_filtered_LockTrqL.append(abs(calc_LockTrq[i]))
                # print("LH:", i, calc_AxleTrqFromOutput[i], calc_AxleTrqFromInput[i])


# Group data [AxleTrq, LockTrq]
# ---------------------- #
data_temp_AxleTrqFromOP_L = []
data_temp_AxleTrqFromIP_L = []
data_plot_AxleTrqFromOP_L = []
data_plot_AxleTrqFromIP_L = []
data_temp_LockTrq_L = []
data_plot_LockTrq_L = []

data_temp_AxleTrqFromOP_R = []
data_temp_AxleTrqFromIP_R = []
data_plot_AxleTrqFromOP_R = []
data_plot_AxleTrqFromIP_R = []
data_temp_LockTrq_R = []
data_plot_LockTrq_R = []

# Loop through each data point
# If the point is within 1 second of the previous point, it should be grouped
# else, move to the next group

# LH Data
print("LH Data Points:", len(data_filtered_LockTrqL))
for i in range(len(data_filtered_LockTrqL)):
    time_between_points = data_filtered_EventTimeL[i] - data_filtered_EventTimeL[i-1]

    if time_between_points > 1 or i == len(data_filtered_LockTrqL)-1:
        # Found the end of the 'group', so calculate average of current temporary lists
        if len(data_temp_AxleTrqFromOP_L) > 0:
            avg_AxleTrqFromOP_L = round(sum(data_temp_AxleTrqFromOP_L) / len(data_temp_AxleTrqFromOP_L), 3)
            data_plot_AxleTrqFromOP_L.append(avg_AxleTrqFromOP_L)
        else:
            continue
        if len(data_temp_AxleTrqFromIP_L) > 0:
            avg_AxleTrqFromIP_L = round(sum(data_temp_AxleTrqFromIP_L) / len(data_temp_AxleTrqFromIP_L), 3)
            data_plot_AxleTrqFromIP_L.append(avg_AxleTrqFromIP_L)
        else:
            continue
        if len(data_temp_LockTrq_L) > 0:
            avg_LockTrq_L = round(sum(data_temp_LockTrq_L) / len(data_temp_LockTrq_L), 3)
            data_plot_LockTrq_L.append(avg_LockTrq_L)
        else:
            continue

        # reset temporary lists
        data_temp_AxleTrqFromOP_L = []
        data_temp_AxleTrqFromIP_L = []
        data_temp_LockTrq_L = []
    else:
        # Still in the same 'group', so add data point to temporary list
        data_temp_AxleTrqFromOP_L.append(data_filtered_AxleTrqFromOP_L[i])
        data_temp_AxleTrqFromIP_L.append(data_filtered_AxleTrqFromIP_L[i])
        data_temp_LockTrq_L.append(data_filtered_LockTrqL[i])

data_plot_LH = pd.DataFrame(data_plot_AxleTrqFromOP_L, columns=['AxleTrqFromOP'])
data_plot_LH['AxleTrqFromIP'] = data_plot_AxleTrqFromIP_L
data_plot_LH['LockTrq'] = data_plot_LockTrq_L
data_plot_LH = data_plot_LH.sort_values('AxleTrqFromOP')
print(data_plot_LH)

# RH Data
print("RH Data Points:", len(data_filtered_LockTrqR))
for i in range(len(data_filtered_LockTrqR)):
    time_between_points = data_filtered_EventTimeR[i] - data_filtered_EventTimeR[i-1]

    if time_between_points > 1 or i == len(data_filtered_LockTrqR)-1:
        # Found the end of the 'group', so calculate average of current temporary lists
        if len(data_temp_AxleTrqFromOP_R) > 0 and len(data_temp_AxleTrqFromOP_R) > sample_rate:
            sum_avg = sum(data_temp_AxleTrqFromOP_R[sample_rate:]) / len(data_temp_AxleTrqFromOP_R[sample_rate:])
            avg_AxleTrqFromOP_R = round(sum_avg, 3)
            data_plot_AxleTrqFromOP_R.append(avg_AxleTrqFromOP_R)
        else:
            continue
        if len(data_temp_AxleTrqFromIP_R) > 0:
            sum_avg = sum(data_temp_AxleTrqFromIP_R[sample_rate:]) / len(data_temp_AxleTrqFromIP_R[sample_rate:])
            avg_AxleTrqFromIP_R = round(sum_avg, 3)
            data_plot_AxleTrqFromIP_R.append(avg_AxleTrqFromIP_R)
        else:
            continue
        if len(data_temp_LockTrq_R) > 0:
            avg_LockTrq_R = round(sum(data_temp_LockTrq_R[sample_rate:]) / len(data_temp_LockTrq_R[sample_rate:]), 3)
            data_plot_LockTrq_R.append(avg_LockTrq_R)
        else:
            continue

        # reset temporary lists
        data_temp_AxleTrqFromOP_R = []
        data_temp_AxleTrqFromIP_R = []
        data_temp_LockTrq_R = []
    else:
        # Still in the same 'group', so add data point to temporary list
        data_temp_AxleTrqFromOP_R.append(data_filtered_AxleTrqFromOP_R[i])
        data_temp_AxleTrqFromIP_R.append(data_filtered_AxleTrqFromIP_R[i])
        data_temp_LockTrq_R.append(data_filtered_LockTrqR[i])

data_plot_RH = pd.DataFrame(data_plot_AxleTrqFromOP_R, columns=['AxleTrqFromOP'])
data_plot_RH['AxleTrqFromIP'] = data_plot_AxleTrqFromIP_R
data_plot_RH['LockTrq'] = data_plot_LockTrq_R
data_plot_RH = data_plot_RH.sort_values('AxleTrqFromOP')
print(data_plot_RH)


# TODO: clean up graphs and plot to PDF report

# Fig 1 - Plot Raw Data & Overlay Filtered Data
# ---------------------- #
fig, ax = plt.subplots(3)

# Fig 1, Plot 1 - Input Torque & Gradient
ax[0].plot(
    data_EventTime,
    data_IPTorque1,
    color="green",
    label="IPTrq",
    marker=None
)

axSecondary = ax[0].twinx()
axSecondary.plot(
    data_EventTime,
    calc_IPTrqGradient,
    color="lightgrey",
    label="IPTrq Gradient",
    marker=None
)
axSecondary.plot(
    data_EventTime,
    calc_IPTrqGradient_smoothed,
    color="darkolivegreen",
    label="IPTrq Gradient Smoothed",
    marker=None
)
ax[0].set_title("Input Torque & Input Torque Delta", loc='left')
ax[0].grid()
ax[0].legend(loc=2)
ax[0].set_xlim([0, max_data_EventTime])
ax[0].set_xlabel("Time [s]")
ax[0].set_ylim([-300, 300])
# axSecondary.set_ylim([-2, 2])
axSecondary.legend(loc=1)
ax[0].set_ylabel("Torque [Nm]")
fig.suptitle(f'Diff Test Overview - {actualGear_hr} Gear', fontsize=16)

# Fig 1, Plot 2 - Axle Torque, Speed and Filtered Data
axSecondary2 = ax[1].twinx()
axSecondary2.plot(
    data_EventTime,
    calc_OPSpeedDelta_smoothed,
    color="lightgray",
    label="OPSpeedDelta",
    marker=None,
    zorder=3
)
axSecondary2.set_ylim([-30, 30])
axSecondary2.legend(loc=1)

ax[1].plot(
    data_EventTime,
    calc_AxleTrqFromOutput,
    color="black",
    label="AxleTrqFromIP",
    marker=None,
    zorder=2
)
ax[1].scatter(
    data_filtered_EventTimeL,
    data_filtered_AxleTrqFromOP_L,
    color="magenta",
    label="Filtered Data L",
    marker=".",
    zorder=1
)
ax[1].scatter(
    data_filtered_EventTimeR,
    data_filtered_AxleTrqFromOP_R,
    color="orange",
    label="Filtered Data R",
    marker=".",
    zorder=1
)
ax[1].set_title("Output Torque, Output Speed Delta & Filtered Data", loc='left')
ax[1].grid()
ax[1].legend(loc=2)
ax[1].set_xlim([0, max_data_EventTime])
ax[1].set_xlabel("Time [s]")
ax[1].set_ylim([-1000, 1000])
ax[1].set_ylabel("Torque [Nm]")

# Fig 1, Plot 3 - Input Speed
ax[2].plot(
    data_EventTime,
    data_IPSpeed1,
    color="red",
    label="IP Speed",
    marker=None
)
ax[2].set_title("Input Speed", loc='left')
ax[2].grid()
ax[2].legend(loc=2)
ax[2].set_xlim([0, max_data_EventTime])
ax[2].set_xlabel("Time [s]")
# ax[2].set_ylim([0, 200])
ax[2].set_ylabel("Speed [rpm]")

# Fig 2, Plot 1 - Diff characterisation plot
fig2, ax2 = plt.subplots()
ax2.plot(
    data_plot_LH['AxleTrqFromOP'],
    data_plot_LH['LockTrq'],
    color="lightgrey",
    label="LH_OP",
    marker="."
)
ax2.plot(
    data_plot_RH['AxleTrqFromOP'],
    data_plot_RH['LockTrq'],
    color="lightgrey",
    label="RH_OP",
    marker="."
)
ax2.plot(
    data_plot_LH['AxleTrqFromIP'],
    data_plot_LH['LockTrq'],
    color="blue",
    label="LH_IP",
    marker="."
)
ax2.plot(
    data_plot_RH['AxleTrqFromIP'],
    data_plot_RH['LockTrq'],
    color="blue",
    label="RH_IP",
    marker="."
)
ax2.set_title(TestName)
ax2.set_xlabel("Axle Torque [Nm]")
ax2.set_ylabel("Locking Torque [Nm]")
ax2.set_xlim([-1000, 1000])
ax2.axes.set_xticks(ticks=[-1000, -800, -600, -400, -200, 0, 200, 400, 600, 800, 1000])
ax2.set_ylim([0, 1000])
ax2.axes.set_yticks(ticks=[0, 200, 400, 600, 800, 1000])
ax2.grid()
ax2.legend(loc=2)


# Fig 3, Plot 1 - Input Torque analysis
fig3, ax3 = plt.subplots(3)

ax3[0].plot(
    data_EventTime,
    data_IPTorque1,
    color="green",
    label="IP Torque",
    marker=None
)
ax3[0].grid()
ax3[0].legend(loc=2)
ax3[0].set_xlim([0, max_data_EventTime])
ax3[0].set_xlabel("Time [s]")
ax3[0].set_ylabel("Torque [Nm]")
ax3[0].axes.set_yticks(ticks=[-232.9, -116.4, -58.2, -29.1, 0, 29.1, 58.2, 116.4, 232.9])

# Fig 3, Plot 2 - Axle torque analysis
ax3[1].plot(
    data_EventTime,
    calc_AxleTrqFromOutput,
    color="black",
    label="AxleTrqFromOP",
    marker=None,
    zorder=10
)
ax3[1].plot(
    data_EventTime,
    calc_AxleTrqFromInput,
    color="red",
    label="AxleTrqFromIP",
    marker=None,
    zorder=10
)
ax3[1].grid()
ax3[1].legend(loc=2)
ax3[1].set_xlim([0, max_data_EventTime])
ax3[1].set_xlabel("Time [s]")
ax3[1].set_ylabel("Torque [Nm]")
ax3[1].axes.set_yticks(ticks=[-800, -400, -200, -100, 0, 100, 200, 400, 800])

# Fig 3, Plot 3 - Output torque analysis
ax3[2].plot(
    data_EventTime,
    data_OPTorque1,
    color="indigo",
    label="OP Torque 1",
    marker=None,
    zorder=2
)
ax3[2].plot(
    data_EventTime,
    data_OPTorque2,
    color="darkviolet",
    label="OP Torque 2",
    marker=None,
    zorder=2
)
ax3[2].plot(
    data_EventTime,
    calc_AxleTrqFromOutput,
    color="lightgrey",
    label="AxleTrqFromOP",
    marker=None,
    zorder=1
)
ax3[2].grid()
ax3[2].legend(loc=2)
ax3[2].set_xlim([0, max_data_EventTime])
ax3[2].set_xlabel("Time [s]")
ax3[2].set_ylabel("Torque [Nm]")
ax3[2].axes.set_yticks(ticks=[-800, -400, -200, -100, 0, 100, 200, 400, 800])

# Fig 4 - Scatter plot of axle torque difference vs input torque. Expecting to see a positive correlation
fig4, ax4 = plt.subplots()
ax4.scatter(
    data_IPTorque1,
    calc_AxleTrqDifference,
    marker=".",
    s=1,
    linewidths=0
)
ax4.scatter(
    data_IPTorque1,
    calc_AxleTrqDifference_IP,
    marker=".",
    s=1,
    linewidths=0
)
ax4.grid()
ax4.set_xlabel("Input Torque [Nm]")
ax4.set_ylabel("Torque [Nm]")

plt.show()
