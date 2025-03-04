import numpy as np
import scipy as sp
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

def slide_func(data, window_size, iter):
    if iter >= window_size:
        if iter % (1 * 512) == 0:
            sliding_window_start = iter - window_size
            sliding_window_end = iter
            sliding_window = np.array(data[sliding_window_start:sliding_window_end])  # sliding_window ~ y
            return sliding_window
        return None
    return None


def filter_data(data):
    # Bandpass filter
    band = [0.5 / (0.5 * 512), 40 / (0.5 * 512)]
    b, a = sp.signal.butter(4, band, btype='band', analog=False, output='ba')
    data = sp.signal.lfilter(b, a, data)

    # plt.hist(data, bins=10, edgecolor='black')
    # filter for EMG by interpolated
    filtered_data = data[(np.abs(data) <= 256)]
    x = np.arange(len(filtered_data))
    interpolated_data = interp1d(x, filtered_data)(np.linspace(0, len(filtered_data) - 1, len(data)))
    return interpolated_data

def hjorth_parameters(signal):
    diff1 = np.diff(signal) # Tính đạo hàm bậc nhất
    diff2 = np.diff(diff1)  # Tính đạo hàm bậc hai

    activity = np.var(signal)      # Activity (A)
    mobility = np.sqrt(np.var(diff1) / activity)  # Mobility (B)
    complexity = np.sqrt(np.var(diff2) / np.var(diff1)) / mobility  # Complexity (C)

    return activity, mobility, complexity


def FeatureExtract(data, plot):
    f, t, Zxx = sp.signal.stft(data, 512, nperseg=15 * 512, noverlap=14 * 512)
    delta = np.array([], dtype=float)
    theta = np.array([], dtype=float)
    alpha = np.array([], dtype=float)
    beta = np.array([], dtype=float)
    for i in range(0, int(t[-1])):
        indices = np.where((f >= 0.5) & (f <= 4))[0]
        delta = np.append(delta, np.sum(np.abs(Zxx[indices, i])))

        indices = np.where((f >= 4) & (f <= 8))[0]
        theta = np.append(theta, np.sum(np.abs(Zxx[indices, i])))

        indices = np.where((f >= 8) & (f <= 13))[0]
        alpha = np.append(alpha, np.sum(np.abs(Zxx[indices, i])))

        indices = np.where((f >= 13) & (f <= 30))[0]
        beta = np.append(beta, np.sum(np.abs(Zxx[indices, i])))

    abr = alpha / beta
    tbr = theta / beta
    dbr = delta / beta
    tar = theta / alpha
    dar = delta / alpha
    dtabr = (alpha + beta) / (delta + theta)

    diction = {"delta": delta,
               "theta": theta,
               "alpha": alpha,
               "beta": beta,
               "abr": abr,
               "tbr": tbr,
               "dbr": dbr,
               "tar": tar,
               "dar": dar,
               "dtabr": dtabr
               }
    if plot == 1:
        # Tạo hình ảnh chính và các hình ảnh con
        fig = plt.figure(figsize=(10, 5))
        # Plot raw
        ax1 = fig.add_subplot(2, 2, 1)
        ax1.plot(data)
        ax1.set_title('EEG Raw Values')
        ax1.set_xlabel('Samples')
        ax1.set_ylabel('RawValue')
        ax1.set_ylim(-256, 256)

        # Plot STFT
        ax2 = fig.add_subplot(1, 2, 2)
        ax2.pcolormesh(t, f, np.abs(Zxx), vmin=-1, vmax=5, shading='auto')
        ax2.set_title('STFT Magnitude')
        ax2.set_xlabel('Time [sec]')
        ax2.set_ylabel('Frequency [Hz]')
        ax2.set_ylim(0.5, 40)

        # Plot brainwave
        ax3 = fig.add_subplot(2, 2, 3)
        ax3.plot(diction['delta'], label="delta")
        ax3.plot(diction['theta'], label="theta")
        ax3.plot(diction['alpha'], label="alpha")
        ax3.plot(diction['beta'], label="beta")
        ax3.set_title('Frequency Bands')
        ax3.set_xlabel('Time [sec]')
        ax3.set_ylabel('Power')
        ax3.set_ylim(0, 400)
        ax3.legend()

        # Hiển thị hình ảnh
        plt.tight_layout()
        plt.savefig("Data_and_AI/test.png")
        plt.close()

    return diction




