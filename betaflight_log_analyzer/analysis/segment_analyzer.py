"""
Module for flight segment identification and analysis
"""
import numpy as np
import pandas as pd
from scipy import signal
import matplotlib.pyplot as plt

class FlightSegmentAnalyzer:
    """Class for identifying and analyzing flight segments"""
    
    def __init__(self, throttle_threshold=1300, min_segment_duration=5.0):
        """
        Initialize the segment analyzer
        
        Args:
            throttle_threshold: Throttle value above which flight is considered active
            min_segment_duration: Minimum duration (in seconds) of a valid flight segment
        """
        self.throttle_threshold = throttle_threshold
        self.min_segment_duration = min_segment_duration
    
    def identify_segments(self, df):
        """
        Identify active flight segments based on throttle values.
        
        Args:
            df: DataFrame containing log data
            
        Returns:
            List of (start_index, end_index) tuples for each segment
        """
        # Check if throttle data is available
        if 'rc_throttle' not in df.columns:
            print("Throttle data not available. Analyzing entire log.")
            return [(0, len(df) - 1)]
        
        # Find segments where throttle is above threshold
        throttle = df['rc_throttle'].values
        active = throttle > self.throttle_threshold
        
        # Find transitions
        transitions = np.where(np.diff(active.astype(int)) != 0)[0] + 1
        transitions = np.insert(transitions, 0, 0)
        transitions = np.append(transitions, len(df))
        
        # Create segments
        segments = []
        sample_rate = 1.0 / (df['time'].iloc[1] - df['time'].iloc[0]) if len(df) > 1 else 1000.0
        min_samples = int(self.min_segment_duration * sample_rate)
        
        for i in range(0, len(transitions) - 1, 2):
            if i+1 < len(transitions):
                start = transitions[i]
                end = transitions[i+1]
                
                # Only include segments longer than min_segment_duration
                if (end - start) > min_samples:
                    segments.append((start, end))
        
        if not segments:
            print("No active flight segments found. Analyzing entire log.")
            return [(0, len(df) - 1)]
        
        print(f"Found {len(segments)} active flight segments.")
        return segments
    
    def analyze_segment(self, df, segment):
        """
        Analyze a single flight segment
        
        Args:
            df: DataFrame containing log data
            segment: Tuple of (start_index, end_index)
            
        Returns:
            Dictionary with analysis results for each axis
        """
        start, end = segment
        segment_df = df.iloc[start:end].copy()
        duration = segment_df['time'].iloc[-1] - segment_df['time'].iloc[0]
        
        results = {}
        axes = ['roll', 'pitch', 'yaw']
        
        for axis in axes:
            # Extract data
            rc_data = segment_df[f'rc_{axis}'].values
            setpoint_data = segment_df[f'setpoint_{axis}'].values
            gyro_data = segment_df[f'gyro_{axis}'].values
            time_data = segment_df['time'].values
            
            # Basic statistics
            rc_stats = {
                'mean': np.mean(rc_data),
                'std': np.std(rc_data),
                'min': np.min(rc_data),
                'max': np.max(rc_data)
            }
            
            setpoint_stats = {
                'mean': np.mean(setpoint_data),
                'std': np.std(setpoint_data),
                'min': np.min(setpoint_data),
                'max': np.max(setpoint_data)
            }
            
            gyro_stats = {
                'mean': np.mean(gyro_data),
                'std': np.std(gyro_data),
                'min': np.min(gyro_data),
                'max': np.max(gyro_data)
            }
            
            # Calculate tracking error
            error = setpoint_data - gyro_data
            error_metrics = {
                'mean': np.mean(np.abs(error)),
                'rms': np.sqrt(np.mean(np.square(error))),
                'peak': np.max(np.abs(error))
            }
            
            # Store results for this axis
            results[axis] = {
                'rc_stats': rc_stats,
                'setpoint_stats': setpoint_stats,
                'gyro_stats': gyro_stats,
                'error_metrics': error_metrics,
                'duration': duration,
                'time': time_data,
                'rc': rc_data,
                'setpoint': setpoint_data,
                'gyro': gyro_data,
                'error': error
            }
            
            # Frequency analysis if we have enough data
            if len(gyro_data) > 1000:
                fs = 1 / (time_data[1] - time_data[0])  # Sampling frequency
                f, pxx = signal.welch(gyro_data, fs, nperseg=1024)
                
                # Find dominant frequency and its power
                peak_idx = np.argmax(pxx)
                peak_freq = f[peak_idx]
                peak_power = pxx[peak_idx]
                
                results[axis]['frequency_analysis'] = {
                    'frequencies': f,
                    'power': pxx,
                    'peak_freq': peak_freq,
                    'peak_power': peak_power
                }
        
        return results 