"""
Module for visualizing advanced analysis results
"""
import os
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from matplotlib.colors import LogNorm

class AdvancedPlotGenerator:
    """Class for generating plots for advanced analysis results"""
    
    def __init__(self, output_dir):
        """
        Initialize the advanced plot generator
        
        Args:
            output_dir: Directory to save plots to
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def _fig_to_base64(self, fig):
        """
        Convert matplotlib figure to base64 string for HTML embedding
        
        Args:
            fig: Matplotlib figure object
            
        Returns:
            Base64 encoded string of the figure
        """
        img_buf = BytesIO()
        # Set legend location explicitly instead of using "best" (default)
        for ax in fig.get_axes():
            legend = ax.get_legend()
            if legend is not None:
                legend.set_loc('upper right')
                
        fig.savefig(img_buf, format='png', dpi=150, bbox_inches='tight')
        img_buf.seek(0)
        img_str = base64.b64encode(img_buf.read()).decode('utf-8')
        plt.close(fig)
        return img_str
    
    def plot_transfer_function(self, tf_data, axis, segment_id):
        """
        Create a Bode plot for the estimated transfer function
        
        Args:
            tf_data: Transfer function data (output from estimate_transfer_function)
            axis: Axis name (roll, pitch, yaw)
            segment_id: Segment identifier
            
        Returns:
            Tuple of (base64 string of the plot, path to saved plot file)
        """
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 12), dpi=150)
        
        # Extract data
        freq = tf_data['frequencies']
        mag = tf_data['magnitude']
        phase = tf_data['phase']
        coherence = tf_data['coherence']
        
        # Plot magnitude response
        ax1.semilogx(freq, 20 * np.log10(mag + 1e-10), 'b-', linewidth=2)
        ax1.set_title(f'{axis.upper()} Axis - Frequency Response Magnitude', fontsize=14)
        ax1.set_xlabel('Frequency (Hz)', fontsize=12)
        ax1.set_ylabel('Magnitude (dB)', fontsize=12)
        ax1.grid(True, which="both", ls="-", alpha=0.7)
        
        # Add gain margin annotation
        try:
            crossover_idx = np.argmin(np.abs(mag - 1.0))
            crossover_freq = freq[crossover_idx]
            ax1.axvline(x=crossover_freq, color='r', linestyle='--', linewidth=1.5,
                        label=f'Crossover: {crossover_freq:.1f}Hz')
            ax1.axhline(y=0, color='g', linestyle='--', linewidth=1.5,
                        label='0dB Line')
            ax1.legend(loc='upper right', fontsize=10)
        except:
            # In case crossover isn't found
            pass
        
        # Plot phase response
        ax2.semilogx(freq, phase, 'r-', linewidth=2)
        ax2.set_title(f'{axis.upper()} Axis - Frequency Response Phase', fontsize=14)
        ax2.set_xlabel('Frequency (Hz)', fontsize=12)
        ax2.set_ylabel('Phase (degrees)', fontsize=12)
        ax2.grid(True, which="both", ls="-", alpha=0.7)
        
        # Highlight phase margin
        try:
            phase_margin = tf_data['phase_margin']
            ax2.axvline(x=crossover_freq, color='r', linestyle='--', linewidth=1.5,
                        label=f'Phase Margin: {phase_margin:.1f}°')
            ax2.axhline(y=-180, color='g', linestyle='--', linewidth=1.5,
                        label='-180°')
            ax2.legend(loc='upper right', fontsize=10)
        except:
            pass
        
        # Plot coherence
        ax3.semilogx(freq, coherence, 'g-', linewidth=2)
        ax3.set_title(f'{axis.upper()} Axis - Input-Output Coherence', fontsize=14)
        ax3.set_xlabel('Frequency (Hz)', fontsize=12)
        ax3.set_ylabel('Coherence', fontsize=12)
        ax3.set_ylim(0, 1.1)
        ax3.grid(True, which="both", ls="-", alpha=0.7)
        
        # Add a threshold line for significant coherence
        ax3.axhline(y=0.8, color='r', linestyle='--', linewidth=1.5,
                    label='Significance Threshold')
        ax3.legend(loc='upper right', fontsize=10)
        
        plt.tight_layout()
        
        # Save the plot and encode for HTML
        plot_path = os.path.join(self.output_dir, f'{axis}_tf_bode_{segment_id}.png')
        plt.savefig(plot_path, dpi=150, bbox_inches='tight')
        img_base64 = self._fig_to_base64(fig)
        
        return img_base64, plot_path
    
    def plot_arx_model(self, arx_data, time_data, setpoint_data, gyro_data, axis, segment_id):
        """
        Plot ARX model identification results
        
        Args:
            arx_data: ARX model data (output from identify_arx_model)
            time_data: Array of time values
            setpoint_data: Array of setpoint values
            gyro_data: Array of gyro values
            axis: Axis name (roll, pitch, yaw)
            segment_id: Segment identifier
            
        Returns:
            Tuple of (base64 string of the plot, path to saved plot file)
        """
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), dpi=150)
        
        # Extract data
        y_pred = arx_data['predicted']
        fit = arx_data['fit']
        step_response = arx_data['step_response']
        
        # Plot actual vs predicted response
        plot_length = min(len(time_data), 5000)  # Limit to 5000 points for clarity
        ax1.plot(time_data[:plot_length], gyro_data[:plot_length], 'b-', 
                label='Actual Gyro', linewidth=2)
        ax1.plot(time_data[:plot_length], y_pred[:plot_length], 'r-', 
                label='ARX Model Prediction', linewidth=2, alpha=0.7)
        ax1.plot(time_data[:plot_length], setpoint_data[:plot_length], 'g--', 
                label='Setpoint', linewidth=1.5, alpha=0.5)
        
        ax1.set_title(f'{axis.upper()} Axis - ARX Model Identification (Fit: {fit:.1f}%)', fontsize=14)
        ax1.set_xlabel('Time (s)', fontsize=12)
        ax1.set_ylabel('Value', fontsize=12)
        ax1.legend(loc='upper right', fontsize=10)
        ax1.grid(True, linestyle='--', alpha=0.7)
        
        # Add a quality assessment
        if fit > 90:
            quality = "Excellent Model Fit"
            color = 'green'
        elif fit > 70:
            quality = "Good Model Fit"
            color = 'blue'
        elif fit > 50:
            quality = "Acceptable Model Fit"
            color = 'orange'
        else:
            quality = "Poor Model Fit"
            color = 'red'
            
        ax1.text(0.02, 0.95, quality, transform=ax1.transAxes, fontsize=12,
                bbox=dict(facecolor=color, alpha=0.2), verticalalignment='top')
        
        # Plot model step response
        step_time = np.arange(len(step_response)) / (len(time_data) / time_data[-1])
        ax2.plot(step_time, step_response, 'b-', linewidth=2)
        ax2.set_title(f'{axis.upper()} Axis - ARX Model Step Response', fontsize=14)
        ax2.set_xlabel('Time (s)', fontsize=12)
        ax2.set_ylabel('Response', fontsize=12)
        ax2.grid(True, linestyle='--', alpha=0.7)
        
        # Add annotations for rise time and settling time if meaningful
        try:
            # Calculate rise time (10% to 90%)
            steady_state = np.mean(step_response[-20:])  # Average of last few points
            if abs(steady_state) > 1e-6:  # Only if there's a meaningful steady state
                rise_10_idx = np.where(step_response >= 0.1 * steady_state)[0][0]
                rise_90_idx = np.where(step_response >= 0.9 * steady_state)[0][0]
                rise_time = step_time[rise_90_idx] - step_time[rise_10_idx]
                
                # Calculate settling time (within 5% of final value)
                settling_band = 0.05 * steady_state
                # Find where it stays within the band
                for i in range(len(step_response) - 30):  # Need 30 samples to confirm settled
                    if all(abs(step_response[i+j] - steady_state) <= settling_band for j in range(30)):
                        settling_time = step_time[i]
                        break
                else:
                    settling_time = None
                
                # Annotate rise time
                ax2.axvspan(step_time[rise_10_idx], step_time[rise_90_idx], color='g', alpha=0.2, 
                           label=f'Rise Time: {rise_time:.3f}s')
                
                # Annotate settling time if found
                if settling_time is not None:
                    ax2.axvline(x=settling_time, color='r', linestyle='--', linewidth=1.5,
                              label=f'Settling Time: {settling_time:.3f}s')
                
                ax2.legend(loc='upper right', fontsize=10)
        except:
            # In case the calculations fail
            pass
        
        plt.tight_layout()
        
        # Save the plot and encode for HTML
        plot_path = os.path.join(self.output_dir, f'{axis}_arx_model_{segment_id}.png')
        plt.savefig(plot_path, dpi=150, bbox_inches='tight')
        img_base64 = self._fig_to_base64(fig)
        
        return img_base64, plot_path
    
    def plot_wavelet_analysis(self, wavelet_data, axis, segment_id):
        """
        Plot wavelet analysis results (time-frequency scalogram)
        
        Args:
            wavelet_data: Wavelet analysis data (output from wavelet_analysis)
            axis: Axis name (roll, pitch, yaw)
            segment_id: Segment identifier
            
        Returns:
            Tuple of (base64 string of the plot, path to saved plot file)
        """
        if wavelet_data is None:
            return None, None
            
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), dpi=150)
        
        # Extract data
        time = wavelet_data['time']
        freq = wavelet_data['frequencies']
        power = wavelet_data['power']
        dom_freqs = wavelet_data['dominant_frequencies']
        
        # Plot scalogram
        # Convert power to dB for better visualization
        power_db = 10 * np.log10(power + 1e-10)
        
        # Create a mesh grid for plotting
        time_mesh, freq_mesh = np.meshgrid(time, freq)
        
        # Plot the scalogram
        c = ax1.pcolormesh(time_mesh, freq_mesh, power_db, cmap='jet', shading='auto')
        
        # Add colorbar
        cbar = plt.colorbar(c, ax=ax1, label='Power (dB)')
        
        # Set frequency axis to log scale for better visualization
        ax1.set_yscale('log')
        ax1.set_ylim(1, 100)  # Focus on 1-100 Hz range
        
        # Highlight frequency bands
        ax1.axhline(y=10, color='w', linestyle='--', linewidth=1, alpha=0.7,
                   label='Low-Mid Boundary (10Hz)')
        ax1.axhline(y=30, color='r', linestyle='--', linewidth=1, alpha=0.7,
                   label='Mid-High Boundary (30Hz)')
        
        ax1.set_title(f'{axis.upper()} Axis - Wavelet Scalogram', fontsize=14)
        ax1.set_xlabel('Time (s)', fontsize=12)
        ax1.set_ylabel('Frequency (Hz)', fontsize=12)
        # Specify legend location explicitly
        ax1.legend(loc='upper right', fontsize=10)
        
        # Plot dominant frequency over time
        ax2.plot(time, dom_freqs, 'b-', linewidth=2)
        ax2.set_title(f'{axis.upper()} Axis - Dominant Frequency Over Time', fontsize=14)
        ax2.set_xlabel('Time (s)', fontsize=12)
        ax2.set_ylabel('Frequency (Hz)', fontsize=12)
        ax2.set_ylim(0, 100)  # Focus on 0-100 Hz range
        ax2.grid(True, linestyle='--', alpha=0.7)
        
        # Highlight frequency bands
        ax2.axhspan(0, 10, color='g', alpha=0.1, label='Low Freq (0-10Hz)')
        ax2.axhspan(10, 30, color='y', alpha=0.1, label='Mid Freq (10-30Hz)')
        ax2.axhspan(30, 100, color='r', alpha=0.1, label='High Freq (30-100Hz)')
        # Specify legend location explicitly
        ax2.legend(loc='upper right', fontsize=10)
        
        # Highlight significant regions
        low_regions = wavelet_data['low_regions']
        mid_regions = wavelet_data['mid_regions']
        high_regions = wavelet_data['high_regions']
        
        # Plot lines at the bottom of the plot for each region type
        for t in low_regions:
            ax2.plot([t, t], [0, 5], 'g-', alpha=0.5, linewidth=3)
        for t in mid_regions:
            ax2.plot([t, t], [0, 5], 'y-', alpha=0.5, linewidth=3)
        for t in high_regions:
            ax2.plot([t, t], [0, 5], 'r-', alpha=0.5, linewidth=3)
        
        plt.tight_layout()
        
        # Save the plot and encode for HTML
        plot_path = os.path.join(self.output_dir, f'{axis}_wavelet_{segment_id}.png')
        plt.savefig(plot_path, dpi=150, bbox_inches='tight')
        img_base64 = self._fig_to_base64(fig)
        
        return img_base64, plot_path
    
    def plot_performance_index(self, perf_data, axis, segment_id):
        """
        Plot performance index results
        
        Args:
            perf_data: Performance data (output from calculate_performance_index)
            axis: Axis name (roll, pitch, yaw)
            segment_id: Segment identifier
            
        Returns:
            Tuple of (base64 string of the plot, path to saved plot file)
        """
        fig, ax = plt.subplots(figsize=(12, 8), dpi=150)
        
        # Extract scores
        tracking = perf_data['tracking_score']
        noise = perf_data['noise_score']
        response = perf_data['response_score']
        overall = perf_data['performance_index']
        
        # Define categories and values
        categories = ['Tracking', 'Noise Reduction', 'Responsiveness', 'Overall']
        values = [tracking, noise, response, overall]
        
        # Define colors based on scores
        def get_color(score):
            if score >= 80:
                return 'green'
            elif score >= 60:
                return 'yellowgreen'
            elif score >= 40:
                return 'orange'
            else:
                return 'red'
                
        colors = [get_color(score) for score in values]
        
        # Create bar chart
        bars = ax.bar(categories, values, color=colors)
        
        # Add value labels on top of each bar
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 2,
                   f'{height:.1f}', ha='center', va='bottom', fontsize=12)
        
        # Add overall performance assessment
        if overall >= 80:
            assessment = "Excellent Performance"
        elif overall >= 60:
            assessment = "Good Performance"
        elif overall >= 40:
            assessment = "Adequate Performance"
        else:
            assessment = "Poor Performance"
        
        ax.text(0.5, 0.95, assessment, transform=ax.transAxes, fontsize=14,
               bbox=dict(facecolor=get_color(overall), alpha=0.2), 
               ha='center', va='top')
        
        # Set chart properties
        ax.set_title(f'{axis.upper()} Axis - Performance Metrics', fontsize=14)
        ax.set_ylabel('Score (0-100)', fontsize=12)
        ax.set_ylim(0, 105)  # Leave room for labels
        
        # Add explanatory note
        note = (
            "Tracking: How well gyro follows setpoint\n"
            "Noise Reduction: How well high-frequency noise is suppressed\n"
            "Responsiveness: How quickly the system responds to inputs\n"
            "Overall: Weighted combination of all metrics"
        )
        ax.text(0.5, -0.15, note, transform=ax.transAxes, fontsize=10,
               ha='center', va='top', bbox=dict(facecolor='white', alpha=0.8))
        
        plt.tight_layout()
        
        # Save the plot and encode for HTML
        plot_path = os.path.join(self.output_dir, f'{axis}_performance_{segment_id}.png')
        plt.savefig(plot_path, dpi=150, bbox_inches='tight')
        img_base64 = self._fig_to_base64(fig)
        
        return img_base64, plot_path 