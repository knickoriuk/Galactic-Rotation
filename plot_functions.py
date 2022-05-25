import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import savgol_filter

def set_plot_style():
    ''' Sets matplotlib's global style settings. '''
    plt.style.use('./light.mplstyle')
    plt.rc('figure', figsize=(12,5), dpi=150)
    plt.rc('axes', titlesize=18)
    plt.rc('savefig', dpi=300, bbox='tight')
    
def plot_keplerian_curve():
    ''' Plots the planets of the solar system's distance from the sun vs 
    orbital velocity along with the 1/sqrt(r) relationship. '''
    R = np.linspace(0.2, 31, 40)
    V = (1.326663e20/(R*1.496e11))**(1/2) /1000
    planets_in = ['Mercury', 'Venus', 'Earth', 'Mars']
    planets_out = ['Jupiter', 'Saturn', 'Uranus', 'Neptune']
    p_in_velocity = [47.9, 35, 29.8, 24.1]
    p_out_velocity = [13.1, 9.7, 6.8, 5.4]
    p_in_radius = [0.3787, 0.72298, 1, 1.51740]
    p_out_radius = [5.19820, 9.5673, 19.2184, 30.11]

    fig, ax = plt.subplots(1,1)
    ax.plot(R, V, lw=1, color='k', ls='--', alpha=0.75)
    ax.scatter(p_in_radius, p_in_velocity, c='red')
    ax.scatter(p_out_radius, p_out_velocity, c='red')
    
    # Inner Planets
    for planet, radius, velocity in zip(planets_in, p_in_radius, p_in_velocity):
        ax.text(radius+0.25, velocity, planet, 
                fontsize=12, 
                family='serif', 
                ha='left', 
                va='center')
    # Outer Planets
    for planet, radius, velocity in zip(planets_out, p_out_radius, p_out_velocity):
        ax.text(radius, velocity+1, planet, 
                fontsize=12, 
                family='serif', 
                ha='center', 
                va='bottom')

    ax.set_title('Keplerian Rotation Curve')
    ax.set_ylabel('Velocity (km/s)')
    ax.set_xlabel('Semimajor Axis (AU)')
    ax.grid()
    ax.text(25, 15, 'v$\propto$R$^{-1/2}$', 
            fontsize=20, 
            family='serif', 
            va='center', 
            ha='center', 
            style='italic')
    return fig, ax

def raw_data_plot(raw_data, l, b):
    ''' Plots the untrimmed and unmodified radio data at longitude l and
    latitude b. '''
    fig, ax = plt.subplots(1,1)
    ax.plot(raw_data['freqs'], 
            raw_data['data'].mean(axis=0).flatten(),
            c='r')
    ax.set_title(f"Galactic Frequency Readings ($\ell={l}$, $b={b}$)")
    ax.set_xlabel("Frequency (MHz)")
    ax.set_ylabel("Signal Measurement")
    ax.grid()
    return fig, ax

def line_plot(df, l, b):
    '''  Plots the data in a dataframe corresponding to a single longitude, 
    comparing the signal for latitude 0 and the non-zero latitude signal. 
    Specify longitude l and latitude b for labelling. '''
    fig, ax = plt.subplots(1,1)
    # Plot data with latitude 0, eg. along the galactic plane
    ax.plot(df.freq,10*np.log10(df.data),
            lw=1, c='red', label='0')
    # Plot data with non-zero latitude
    ax.plot(df.freq,10*np.log10(df.baseline),
        lw=0.5, c='black', ls='--', label=str(b))
    
    ax.legend(title='Galatic Latitude (b)')
    ax.set_xlabel('Frequency (MHz)')
    ax.set_ylabel('Power (dB, arbitrary)')
    ax.set_title(f"Galactic Frequency Readings ($\ell={l}$)")
    ax.grid()
    ax.set_xlim(1416, 1425.5)
    ax.set_ylim(63, 67)
    return fig, ax

def plot_baseline_fit(df, l, deg=13):
    ''' Plots the ratio of on-plane signal to off-plane signal, highlighting 
    the points within 0.5 to the 21cm line. Specify longitude l for labelling,
    and a polynomial degree for best fit line.'''
    f21cm = 1420.405 #MHz
    df_trimmed = df.drop(df[np.abs(df.freq-f21cm) < 0.5].index)
    norm_trimmed = df_trimmed.data/df_trimmed.baseline
    norm = df.data/df.baseline
    
    fit_coeff = np.polyfit(df_trimmed.freq.tolist(), norm_trimmed.tolist(), deg)
    fit = np.polyval(fit_coeff, df.freq.tolist())
    
    fig, ax = plt.subplots(1,1)
    ax.scatter(df.freq, norm, s=10, c='white', ec='blue', label="Points within 0.5MHz of the 21-cm line")
    ax.scatter(df_trimmed.freq, norm_trimmed, s=10, c='red', label="Remaining data points")
    ax.plot(df.freq, fit, color='k')
    ax.grid()
    ax.legend()
    ax.set_title(f'Ratio of On-Plane Signal to Off-Plane Signal ($\ell={l}$)')
    ax.set_xlabel('Frequency (MHz)')
    ax.set_ylabel('Normalized Ratio of Signals')
    return fig, ax

def detrend(df):
    ''' Given a dataset, calculates a polynomial fit for data not within 0.5 of
    the 21cm line and subtracts the fit from the data, such that the points lie 
    on and around 0. '''
    f21cm = 1420.405 #MHz
    df_trimmed = df.drop(df[np.abs(df.freq-f21cm) < 0.5].index)
    norm_trimmed = df_trimmed.data/df_trimmed.baseline
    norm = df.data/df.baseline
    
    fit_coeff = np.polyfit(df_trimmed.freq.tolist(), norm_trimmed.tolist(), 13)
    fit = np.polyval(fit_coeff, df.freq.tolist())
    return norm-fit

def plot_detrended_freq(df, corrected_signal, l):
    ''' Plots the ratio of on-plane signal to off-plane signal with the 
    polynomial trendline subtracted from the points. '''
    fig, ax = plt.subplots(1,1)
    ax.grid(which = 'major', alpha=0.5, lw=0.75, c='k')
    ax.grid(which = 'minor', alpha=0.25, lw=0.25, ls='--', c='k')
    ax.axhline(0, c='k', ls='-', lw=0.5, zorder=3.5)
    
    x = df.freq
    ax.plot(x, corrected_signal, lw=1, c='red')
    
    ax.set_ylabel('Fractional Power Difference (%)')
    ax.set_title(f'Radio Signal Increase Within Galactic Plane ($\ell={l}$)')
    ax.set_xlabel('Frequency (MHz)')
    return fig, ax

def freq_to_rv(frequency_array):
    ''' Converts a frequency to radial velocity, given the frequency was 
    shifted from the 21-cm line. '''
    f21cm = 1420.405 #MHz
    rv = 2.99792e8 * (f21cm - frequency_array)/frequency_array
    return rv

def plot_normalized_signal(df, corrected_signal, l, zoomed=False):    
    ''' Plots the ratio of on-plane signal to off-plane signal, converted to a
    radial velocity measurement. '''
    fig, ax = plt.subplots(1,1)
    ax.set_ylabel('Fractional Power Difference (%)')
    ax.set_title(f'Radial Velocity of Galactic Arms Based on Shifting of 21-cm Line ($\ell={l}$)')

    ax.grid(which = 'major', alpha=0.5, lw=0.75, c='k')
    ax.grid(which = 'minor', alpha=0.25, lw=0.25, ls='--', c='k')
    ax.axhline(0, c='k', ls='-', lw=0.5, zorder=3.5)
    
    x = freq_to_rv(df.freq) * 10e-4
    ax.plot(x, corrected_signal, lw=1, c='red')
    ax.set_xlabel('Radial Velocity (km/s)')
    ax.minorticks_on()
    
    ax2 = ax.twiny()
    x = df.freq
    ax2.plot(x, corrected_signal, lw=0)
    ax2.set_xlabel('Frequency (MHz)')
    ax2.minorticks_on()

    if zoomed==True:
        ax.set_xlim(freq_to_rv(1423)*10e-4, freq_to_rv(1418)*10e-4)
        ax2.set_xlim(1423, 1418)
        
    return fig, ax, ax2

def plot_rv_heatmap(all_datasets):
    ''' Generates a heatmap of radial velocity measurements for each longitude
    that data is available for. '''
    power = []
    for df in all_datasets.values():
        power.append(detrend(df))
    rvs = freq_to_rv(all_datasets[10].freq)
    
    y = rvs * 10e-4
    fig, ax = plt.subplots(1,1, figsize=[10,5])
    c = ax.contourf(np.transpose(power), cmap='inferno',
                  extent=[7, 194, np.max(y), np.min(y)],
                  origin='lower', levels=np.linspace(-0.0, 0.0575, 100), 
                  extend='both')
    
    ax.set_ylim(-275, 250)
    ax.set_title('Radial Velocity Detected At Galactic Longitudes')
    ax.set_ylabel("Radial Velocity (km/s)")
    ax.set_xlabel("Galactic Longitude")
    ax.set_xticks([10, 30, 50, 70, 90, 110, 130, 150, 170, 190])
    fig.colorbar(c, ax=ax, label="Fractional Power Difference (%)", 
                 ticks=[0, 0.01, 0.02, 0.03, 0.04, 0.05])
    return fig, ax

def get_tangential_velocity(v_radial, l):
    ''' Calculates the ring radius and tangential velocity given radial 
    velocity and the galactic longitude of the data measurement.'''
    R_sun = 8 #kpc
    v_sun = 220 #km/s
    l_rad = l * np.pi / 180
    R = R_sun * np.sin(l_rad)
    v = v_radial + v_sun * np.sin(l_rad)
    return (R, v)

def plot_rotation_curve(vr_peaks_array, longitudes, comparison=False):
    ''' Plots a rotation curve for the Milky Way given a list of radial 
    velocities corresponding to the strongest signal/highest peak, and a list 
    of longitudes. Overlays the plot with the three rotation models when 
    comparison==True. '''
    R = []
    v = []
    for i in range(16):
        results = get_tangential_velocity(vr_peaks_array[i], longitudes[i])
        R.append(results[0])
        v.append(results[1])
    
    fig, ax = plt.subplots(1,1)
    ax.set_ylabel('Velocity (km/s)')
    ax.set_xlabel('Distance to Galactic Core (kpc)')
    ax.set_title('Milky Way Rotation Curve')
    ax.grid()
    
    if comparison==False:
        ax.plot(R, v, color='red', lw=1.5, marker='x', label='Milky Way Data')
    
    else:
        ax.scatter(R, v, marker='*', s=75, color='white', ec='red', lw=0.75, 
                   label='Milky Way Data')
        ax.plot(R, savgol_filter(v, 9, 3), color='red', lw=10, alpha=0.25)
        
        solid_x = [1.75, 5.25]
        solid_y = [0, 200]
        ax.plot(solid_x, solid_y, color='#ac26ff', lw=1.5, ls='--', 
                label='Solid Body Rotation (v $\propto$ R)')  
        
        kepler_x = np.linspace(4, 8.25, 20)
        kepler_y = 410 * kepler_x ** (-1/2)
        ax.plot(kepler_x, kepler_y, color='#0091ff', lw=1.5, ls='--', 
                label='Keplerian Rotation (v $\propto$ R$^{-1/2}$)')
        
        flat_x = [3.25, 8]
        flat_y = [185, 185]
        ax.plot(flat_x, flat_y, lw=1.5, color='#00b324', ls='--', 
                label='Differential Rotation (v = constant)')
        
        ax.legend(loc='lower right')
    return fig, ax