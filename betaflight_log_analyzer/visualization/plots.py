"""
Module for visualization functions
"""
import os
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
import base64

def fig_to_base64(fig):
    """
    Convert matplotlib figure to base64 string for HTML embedding
    
    Args:
        fig: Matplotlib figure object
        
    Returns:
        Base64 encoded string of the figure
    """
    img_buf = BytesIO()
    fig.savefig(img_buf, format='png', dpi=150, bbox_inches='tight')
    img_buf.seek(0)
    img_str = base64.b64encode(img_buf.read()).decode('utf-8')
    plt.close(fig)
    return img_str

class PlotGenerator:
    """Class for generating plots from flight data"""
    
    def __init__(self, output_dir):
        """
        Initialize the plot generator
        
        Args:
            output_dir: Directory to save plots to
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def plot_time_domain(self, time_data, setpoint_data, gyro_data, error_data, 
                        axis, segment_id, error_rms):
        """
        Create an enhanced time domain plot with tuning quality indicators
        
        Args:
            time_data: Array of time values
            setpoint_data: Array of setpoint values
            gyro_data: Array of gyro values
            error_data: Array of error values
            axis: Axis name (roll, pitch, yaw)
            segment_id: Segment identifier
            error_rms: RMS error value
            
        Returns:
            Tuple of (base64 string of the plot, path to saved plot file)
        """
        # Determine how much data to plot
        plot_length = min(5000, len(time_data))
        
        # Create figure with higher resolution
        fig = plt.figure(figsize=(12, 8), dpi=150)
        
        # Plot setpoint and gyro with thicker lines
        plt.plot(time_data[:plot_length], setpoint_data[:plot_length], 'b-', 
                label='Setpoint', linewidth=2)
        plt.plot(time_data[:plot_length], gyro_data[:plot_length], 'r-', 
                label='Gyro Response', linewidth=2)
        
        # Plot error
        plt.plot(time_data[:plot_length], error_data[:plot_length], 'g-', 
                label='Error', linewidth=1.5, alpha=0.7)
        
        # Add horizontal band showing acceptable error range
        plt.axhspan(-10, 10, color='green', alpha=0.1, label='Ideal Error Range')
        
        # Add visual quality indicators
        if error_rms < 10:
            quality = "GOOD"
            color = 'green'
        elif error_rms < 30:
            quality = "ACCEPTABLE"
            color = 'orange'
        else:
            quality = "NEEDS TUNING"
            color = 'red'
        
        # Add quality text in top left corner
        plt.text(time_data[1], max(max(setpoint_data[:plot_length]), max(gyro_data[:plot_length])) * 0.9, 
                f"Tuning Quality: {quality}\nRMS Error: {error_rms:.1f}", 
                fontsize=12, bbox=dict(facecolor=color, alpha=0.2))
        
        # Add better labels and styling
        plt.xlabel('Time (seconds)', fontsize=12)
        plt.ylabel('Value', fontsize=12)
        plt.title(f'{axis.upper()} Axis Response - Segment {segment_id}', fontsize=14)
        plt.legend(loc='upper right', fontsize=10)
        plt.grid(True, linestyle='--', alpha=0.7)
        
        # Add annotations for overshoot and delay
        if max(abs(error_data[:plot_length])) > 15:
            peak_error_idx = np.argmax(abs(error_data[:plot_length]))
            plt.annotate('Peak Error', 
                        xy=(time_data[peak_error_idx], error_data[peak_error_idx]),
                        xytext=(time_data[peak_error_idx], error_data[peak_error_idx] * 1.2),
                        arrowprops=dict(facecolor='black', shrink=0.05, width=1.5),
                        fontsize=10)
        
        # Save figure and embed in HTML
        plot_path = os.path.join(self.output_dir, f'{axis}_segment_{segment_id}.png')
        plt.savefig(plot_path, dpi=150, bbox_inches='tight')
        
        # Create base64 version for HTML embedding
        img_base64 = fig_to_base64(fig)
        plt.close(fig)
        
        return img_base64, plot_path
    
    def plot_psd(self, frequencies, power, peak_freq, peak_power, axis, segment_id):
        """
        Create an enhanced PSD plot with oscillation indicators
        
        Args:
            frequencies: Array of frequency values
            power: Array of power spectral density values
            peak_freq: Dominant frequency
            peak_power: Power of dominant frequency
            axis: Axis name (roll, pitch, yaw)
            segment_id: Segment identifier
            
        Returns:
            Tuple of (base64 string of the plot, path to saved plot file)
        """
        fig = plt.figure(figsize=(12, 8), dpi=150)
        
        # Use a more visually distinct color scheme
        plt.semilogy(frequencies, power, linewidth=2, color='darkblue')
        
        # Highlight different frequency ranges
        plt.axvspan(0, 10, color='green', alpha=0.1, label='Low Freq (<10Hz)')
        plt.axvspan(10, 30, color='orange', alpha=0.1, label='Mid Freq (10-30Hz)')
        plt.axvspan(30, 100, color='red', alpha=0.1, label='High Freq (>30Hz)')
        
        # Mark peak frequency
        plt.axvline(x=peak_freq, color='r', linestyle='--', linewidth=2, 
                    label=f'Peak: {peak_freq:.1f}Hz')
        
        # Add annotations for peak
        plt.annotate(f'Peak Power: {peak_power:.1f}',
                    xy=(peak_freq, peak_power),
                    xytext=(peak_freq * 1.2, peak_power * 1.2),
                    arrowprops=dict(facecolor='black', shrink=0.05, width=1.5),
                    fontsize=10)
        
        # Add interpretations based on peak frequency
        if peak_freq < 10:
            interpretation = "Low frequency peaks may indicate P too high or I too low"
            color = 'green'
        elif peak_freq < 30:
            interpretation = "Mid frequency peaks may indicate P tuning issues"
            color = 'orange'
        else:
            interpretation = "High frequency peaks may indicate D too high or noise issues"
            color = 'red'
        
        # Add interpretation text
        plt.annotate(interpretation,
                    xy=(0.5, 0.02),
                    xycoords='figure fraction',
                    bbox=dict(facecolor=color, alpha=0.2),
                    fontsize=10)
        
        # Add better labels and styling
        plt.xlabel('Frequency (Hz)', fontsize=12)
        plt.ylabel('Power Spectral Density (power/Hz)', fontsize=12)
        plt.title(f'{axis.upper()} Axis - Frequency Analysis - Segment {segment_id}', fontsize=14)
        plt.legend(loc='upper right', fontsize=10)
        plt.grid(True, linestyle='--', alpha=0.7)
        
        # Save figure and embed in HTML
        psd_path = os.path.join(self.output_dir, f'{axis}_psd_segment_{segment_id}.png')
        plt.savefig(psd_path, dpi=150, bbox_inches='tight')
        
        # Create base64 version for HTML embedding
        img_base64 = fig_to_base64(fig)
        plt.close(fig)
        
        return img_base64, psd_path 