"""
Module for advanced analysis techniques for Betaflight logs
"""
import numpy as np
from scipy import signal, linalg
import matplotlib.pyplot as plt
import pandas as pd
try:
    import pywt  # PyWavelets for wavelet analysis
except ImportError:
    pywt = None

class AdvancedAnalyzer:
    """Class for advanced analysis of flight data"""
    
    def __init__(self):
        """Initialize the advanced analyzer"""
        # Check if PyWavelets is available
        self.wavelet_available = pywt is not None
        if not self.wavelet_available:
            print("Warning: PyWavelets not installed. Wavelet analysis not available.")
            print("Install with: pip install PyWavelets")
    
    def estimate_transfer_function(self, time_data, setpoint_data, gyro_data):
        """
        Estimate the transfer function of the system using frequency domain techniques
        
        Args:
            time_data: Array of time values
            setpoint_data: Array of setpoint values (input)
            gyro_data: Array of gyro values (output)
            
        Returns:
            Dictionary with transfer function data
        """
        # Calculate sampling frequency
        dt = np.mean(np.diff(time_data))
        fs = 1/dt  # Sampling frequency
        
        # Calculate frequency response using Welch's method
        freq, Pxx_setpoint = signal.welch(setpoint_data, fs, nperseg=1024)
        freq, Pxx_gyro = signal.welch(gyro_data, fs, nperseg=1024)
        
        # Calculate cross-spectral density
        freq, Pxy = signal.csd(setpoint_data, gyro_data, fs, nperseg=1024)
        
        # Calculate transfer function estimate
        H = Pxy / (Pxx_setpoint + 1e-10)  # Add small value to avoid division by zero
        H_mag = np.abs(H)
        H_phase = np.angle(H, deg=True)
        
        # Calculate coherence (measure of linear relationship between input and output)
        freq, coherence = signal.coherence(setpoint_data, gyro_data, fs, nperseg=1024)
        
        # Extract frequency response characteristics
        # Find gain margin and phase margin areas
        crossover_idx = np.argmin(np.abs(H_mag - 1.0))
        phase_at_crossover = H_phase[crossover_idx]
        phase_margin = 180 + phase_at_crossover if phase_at_crossover < 0 else 180 - phase_at_crossover
        
        # Find resonant frequencies (peaks in magnitude response)
        # Ignore very low frequencies
        start_idx = np.argmax(freq > 1.0)
        peaks, _ = signal.find_peaks(H_mag[start_idx:])
        peaks += start_idx
        
        resonant_freqs = []
        if len(peaks) > 0:
            # Only consider peaks with significant magnitude
            significant_peaks = [p for p in peaks if H_mag[p] > 1.1]
            resonant_freqs = [(freq[p], H_mag[p]) for p in significant_peaks]
        
        return {
            'frequencies': freq,
            'magnitude': H_mag,
            'phase': H_phase,
            'coherence': coherence,
            'phase_margin': phase_margin,
            'resonant_frequencies': resonant_freqs
        }
    
    def identify_arx_model(self, time_data, setpoint_data, gyro_data, na=4, nb=4, nk=1):
        """
        Identify an ARX (AutoRegressive with eXogenous input) model of the system
        
        Args:
            time_data: Array of time values
            setpoint_data: Array of setpoint values (input)
            gyro_data: Array of gyro values (output)
            na: Order of the AR part
            nb: Order of the input part
            nk: Delay
            
        Returns:
            Dictionary with ARX model parameters and fit quality
        """
        try:
            # Ensure arrays are properly shaped
            y = gyro_data.flatten()
            u = setpoint_data.flatten()
            
            # Ensure we have enough data points for ARX modeling
            N = len(y)
            if N <= na + nb:
                print("Not enough data points for ARX modeling")
                return self._create_dummy_arx_result(N)
            
            # Construct data matrices
            phi = np.zeros((N-na, na+nb))
            
            for i in range(N-na):
                # AR part - fixed slicing to properly fill the array
                for j in range(na):
                    if i+na-1-j >= 0:
                        phi[i, j] = -y[i+na-1-j]
                    else:
                        phi[i, j] = 0
                
                # Input part (with delay)
                for j in range(nb):
                    idx = i+na-nk-j
                    if idx >= 0 and idx < N:
                        phi[i, na+j] = u[idx]
                    else:
                        phi[i, na+j] = 0
            
            # Output vector
            Y = y[na:]
            
            # Least squares estimation of parameters
            try:
                theta = linalg.lstsq(phi, Y)[0]
            except Exception as e:
                print(f"Error in ARX parameter estimation: {e}")
                return self._create_dummy_arx_result(N)
            
            # Model output prediction
            y_pred = np.zeros_like(y)
            y_pred[:na] = y[:na]  # Initial conditions
            
            for i in range(na, N):
                # AR part
                ar_part = 0
                for j in range(na):
                    ar_part -= theta[j] * y_pred[i-j-1]
                    
                # Input part
                input_part = 0
                for j in range(nb):
                    idx = i-j-nk
                    if idx >= 0:
                        input_part += theta[na+j] * u[idx]
                
                y_pred[i] = ar_part + input_part
            
            # Calculate fit percentage (normalized root mean square error)
            fit = 100 * (1 - np.linalg.norm(y-y_pred) / np.linalg.norm(y-np.mean(y)))
            
            # Extract dynamics characteristics from the model
            # A(q)y(t) = B(q)u(t-nk)
            # A(q) = 1 + a1*q^-1 + ... + ana*q^-na
            # B(q) = b1*q^-1 + ... + bnb*q^-nb
            A = np.concatenate(([1.0], theta[:na]))
            B = theta[na:]
            
            # Calculate step response from the model
            step_length = 200
            step_input = np.ones(step_length)
            step_output = np.zeros(step_length)
            
            # Initial conditions
            for i in range(na):
                step_output[i] = 0
            
            # Calculate step response
            for i in range(na, step_length):
                # AR part
                ar_part = 0
                for j in range(na):
                    ar_part -= A[j+1] * step_output[i-j-1]
                    
                # Input part (with delay)
                input_part = 0
                for j in range(nb):
                    idx = i-j-nk
                    if idx >= 0 and idx < step_length:
                        input_part += B[j] * step_input[idx]
                
                step_output[i] = ar_part + input_part
            
            return {
                'parameters': theta,
                'A': A,
                'B': B,
                'fit': fit,
                'predicted': y_pred,
                'step_response': step_output
            }
        except Exception as e:
            print(f"Error in ARX model identification: {e}")
            return self._create_dummy_arx_result(len(gyro_data))
    
    def _create_dummy_arx_result(self, N):
        """Create a dummy ARX result when the real computation fails"""
        # Create a simple dummy model that can be displayed without errors
        dummy_len = min(N, 200)
        dummy_step = np.zeros(dummy_len)
        dummy_step[10:] = 1.0  # Simple step at t=10
        
        return {
            'parameters': np.zeros(8),  # na=4, nb=4
            'A': np.array([1.0, 0, 0, 0, 0]),
            'B': np.zeros(4),
            'fit': 0.0,
            'predicted': np.zeros(N),
            'step_response': dummy_step
        }
    
    def wavelet_analysis(self, time_data, gyro_data):
        """
        Perform wavelet analysis to detect time-varying oscillations
        
        Args:
            time_data: Array of time values
            gyro_data: Array of gyro values
            
        Returns:
            Dictionary with wavelet analysis results or None if PyWavelets not available
        """
        if not self.wavelet_available:
            print("Wavelet analysis requires PyWavelets package. Install with: pip install PyWavelets")
            return None
        
        # Sampling frequency
        dt = np.mean(np.diff(time_data))
        fs = 1/dt
        
        # Remove mean from the signal
        data = gyro_data - np.mean(gyro_data)
        
        # Perform continuous wavelet transform
        scales = np.arange(1, 128)
        wavelet = 'morl'  # Morlet wavelet
        
        # Compute CWT
        coef, freqs = pywt.cwt(data, scales, wavelet, 1.0/fs)
        
        # Convert scales to frequencies
        frequencies = pywt.scale2frequency(wavelet, scales) * fs
        
        # Calculate wavelet power
        power = np.abs(coef)**2
        
        # Find dominant frequencies over time
        dominant_scales = np.argmax(power, axis=0)
        dominant_freqs = frequencies[dominant_scales]
        
        # Find regions with significant oscillations
        # We'll define these as regions where the power exceeds a threshold
        # and the dominant frequency is within certain bands
        power_threshold = np.mean(power) + 2 * np.std(power)
        max_power_over_time = np.max(power, axis=0)
        
        # Define frequency bands
        low_band = (2, 10)   # 2-10 Hz: low frequency oscillations
        mid_band = (10, 30)  # 10-30 Hz: mid frequency oscillations
        high_band = (30, 100) # 30-100 Hz: high frequency oscillations
        
        # Find regions with significant oscillations in each band
        def find_oscillation_regions(freqs, power_over_time, band, threshold):
            mask = (freqs >= band[0]) & (freqs < band[1])
            if not np.any(mask):
                return []
                
            band_power = np.max(power[:, mask], axis=1)
            significant = band_power > threshold
            
            # Find continuous regions
            regions = []
            start = None
            for i, sig in enumerate(significant):
                if sig and start is None:
                    start = i
                elif not sig and start is not None:
                    regions.append((start, i))
                    start = None
            
            # Add last region if it extends to the end
            if start is not None:
                regions.append((start, len(significant)))
                
            return regions
        
        low_regions = []
        mid_regions = []
        high_regions = []
        
        for i, freq in enumerate(dominant_freqs):
            if max_power_over_time[i] > power_threshold:
                if low_band[0] <= freq < low_band[1]:
                    low_regions.append(i)
                elif mid_band[0] <= freq < mid_band[1]:
                    mid_regions.append(i)
                elif high_band[0] <= freq < high_band[1]:
                    high_regions.append(i)
        
        # Convert indices to time values
        low_regions_time = [time_data[i] for i in low_regions]
        mid_regions_time = [time_data[i] for i in mid_regions]
        high_regions_time = [time_data[i] for i in high_regions]
        
        return {
            'time': time_data,
            'frequencies': frequencies,
            'power': power,
            'dominant_frequencies': dominant_freqs,
            'low_regions': low_regions_time,
            'mid_regions': mid_regions_time,
            'high_regions': high_regions_time
        }
    
    def calculate_performance_index(self, time_data, setpoint_data, gyro_data):
        """
        Calculate a comprehensive performance index based on multiple metrics
        
        Args:
            time_data: Array of time values
            setpoint_data: Array of setpoint values
            gyro_data: Array of gyro values
            
        Returns:
            Dictionary with performance metrics
        """
        # Calculate tracking error
        error = setpoint_data - gyro_data
        
        # Basic error statistics
        error_mean = np.mean(np.abs(error))
        error_rms = np.sqrt(np.mean(np.square(error)))
        error_peak = np.max(np.abs(error))
        
        # Calculate frequency content
        fs = 1 / np.mean(np.diff(time_data))
        f, pxx = signal.welch(gyro_data, fs, nperseg=1024)
        
        # Find dominant frequency and its power
        peak_idx = np.argmax(pxx)
        peak_freq = f[peak_idx]
        peak_power = pxx[peak_idx]
        
        # Calculate high-frequency energy ratio (indicator of noise/vibration)
        high_freq_idx = f > 30
        if np.any(high_freq_idx):
            high_freq_energy = np.sum(pxx[high_freq_idx])
            total_energy = np.sum(pxx)
            high_freq_ratio = high_freq_energy / total_energy if total_energy > 0 else 0
        else:
            high_freq_ratio = 0
        
        # Calculate responsiveness (cross-correlation between setpoint and gyro)
        corr = np.correlate(setpoint_data, gyro_data, mode='full')
        corr_max = np.max(corr)
        corr_lag = np.argmax(corr) - len(setpoint_data) + 1
        responsiveness = corr_max / (np.std(setpoint_data) * np.std(gyro_data) * len(setpoint_data))
        
        # Normalize all metrics to 0-100 scale (higher is better)
        tracking_score = max(0, 100 - error_rms * 2)  # Perfect tracking = 100
        noise_score = max(0, 100 - high_freq_ratio * 500)  # No noise = 100
        response_score = max(0, responsiveness * 100)  # Perfect correlation = 100
        
        # Overall performance index (weighted average)
        performance_index = (tracking_score * 0.5 + 
                            noise_score * 0.3 + 
                            response_score * 0.2)
        
        return {
            'tracking_score': tracking_score,
            'noise_score': noise_score,
            'response_score': response_score,
            'performance_index': performance_index,
            'error_mean': error_mean,
            'error_rms': error_rms,
            'error_peak': error_peak,
            'peak_freq': peak_freq,
            'high_freq_ratio': high_freq_ratio,
            'responsiveness': responsiveness,
            'corr_lag': corr_lag
        } 