#!/usr/bin/env python3

import sys
import os
import subprocess
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import signal
import re
import time
import datetime
import base64
from io import BytesIO

# Path to blackbox_decode tool
BLACKBOX_DECODE = "/Users/yurym/github/blackbox-tools/obj/blackbox_decode"

def decode_blackbox_log(file_path):
    """
    Decode a Betaflight blackbox log using blackbox_decode.
    Returns the path to the decoded CSV file.
    """
    try:
        # Get the directory and filename
        log_dir = os.path.dirname(file_path)
        log_basename = os.path.basename(file_path)
        
        # Create the output directory
        output_dir = os.path.join(log_dir, "csv")
        os.makedirs(output_dir, exist_ok=True)
        
        # Run blackbox_decode with the full path
        print(f"Decoding log file: {file_path}")
        print(f"Using blackbox_decode from: {BLACKBOX_DECODE}")
        
        result = subprocess.run(
            [BLACKBOX_DECODE, "--stdout", file_path],
            capture_output=True,
            text=True
        )
        
        # Check if the command was successful
        if result.returncode != 0:
            print(f"Error decoding log: {result.stderr}")
            return None
        
        # Save the output to a CSV file
        csv_path = os.path.join(output_dir, log_basename + ".csv")
        with open(csv_path, 'w') as f:
            f.write(result.stdout)
        
        print(f"Decoded log saved to: {csv_path}")
        return csv_path
    
    except Exception as e:
        print(f"Error decoding log: {e}")
        return None

def read_blackbox_log(file_path):
    """
    Read a Betaflight blackbox log and return a pandas DataFrame.
    Handles both raw logs and pre-decoded CSV files.
    """
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return None
        
        # Check if it's a CSV file
        if file_path.lower().endswith('.csv'):
            df = pd.read_csv(file_path, low_memory=False)
        else:
            # Try to decode the log file
            csv_path = decode_blackbox_log(file_path)
            if csv_path is None:
                return None
            
            # Read the CSV file
            df = pd.read_csv(csv_path, low_memory=False)
        
        # Map column names
        column_mapping = {
            'loopIteration': 'loopIteration',
            ' time (us)': 'time',
            ' axisP[0]': 'P_roll',
            ' axisP[1]': 'P_pitch',
            ' axisP[2]': 'P_yaw',
            ' axisI[0]': 'I_roll',
            ' axisI[1]': 'I_pitch',
            ' axisI[2]': 'I_yaw',
            ' axisD[0]': 'D_roll',
            ' axisD[1]': 'D_pitch',
            ' axisF[0]': 'F_roll',
            ' axisF[1]': 'F_pitch',
            ' axisF[2]': 'F_yaw',
            ' rcCommand[0]': 'rc_roll',
            ' rcCommand[1]': 'rc_pitch',
            ' rcCommand[2]': 'rc_yaw',
            ' rcCommand[3]': 'rc_throttle',
            ' setpoint[0]': 'setpoint_roll',
            ' setpoint[1]': 'setpoint_pitch',
            ' setpoint[2]': 'setpoint_yaw',
            ' gyroADC[0]': 'gyro_roll',
            ' gyroADC[1]': 'gyro_pitch',
            ' gyroADC[2]': 'gyro_yaw'
        }
        
        # Rename columns that exist in the DataFrame
        for old_name, new_name in column_mapping.items():
            if old_name in df.columns:
                df = df.rename(columns={old_name: new_name})
        
        # Convert time to seconds
        if 'time' in df.columns:
            df['time'] = (df['time'] - df['time'].iloc[0]) / 1000000.0
        
        return df
    
    except Exception as e:
        print(f"Error reading log file: {e}")
        return None

def identify_flight_segments(df, throttle_threshold=1300):
    """
    Identify active flight segments based on throttle values.
    Returns a list of (start_index, end_index) tuples.
    """
    # Check if throttle data is available
    if 'rc_throttle' not in df.columns:
        print("Throttle data not available. Analyzing entire log.")
        return [(0, len(df) - 1)]
    
    # Find segments where throttle is above threshold
    throttle = df['rc_throttle'].values
    active = throttle > throttle_threshold
    
    # Find transitions
    transitions = np.where(np.diff(active.astype(int)) != 0)[0] + 1
    transitions = np.insert(transitions, 0, 0)
    transitions = np.append(transitions, len(df))
    
    # Create segments
    segments = []
    for i in range(0, len(transitions) - 1, 2):
        if i+1 < len(transitions):
            start = transitions[i]
            end = transitions[i+1]
            
            # Only include segments longer than 5 seconds
            if (end - start) > 5 * 1000:  # Assuming 1kHz logging rate
                segments.append((start, end))
    
    if not segments:
        print("No active flight segments found. Analyzing entire log.")
        return [(0, len(df) - 1)]
    
    print(f"Found {len(segments)} active flight segments.")
    return segments

def fig_to_base64(fig):
    """Convert matplotlib figure to base64 string for HTML embedding"""
    img_buf = BytesIO()
    fig.savefig(img_buf, format='png', dpi=150, bbox_inches='tight')
    img_buf.seek(0)
    img_str = base64.b64encode(img_buf.read()).decode('utf-8')
    plt.close(fig)
    return img_str

def plot_time_domain(time_data, setpoint_data, gyro_data, axis, segment_id, output_dir, error_rms):
    """Create an enhanced time domain plot with tuning quality indicators"""
    # Determine how much data to plot
    plot_length = min(5000, len(time_data))
    
    # Create figure with higher resolution
    fig = plt.figure(figsize=(12, 8), dpi=150)
    
    # Plot setpoint and gyro with thicker lines
    plt.plot(time_data[:plot_length], setpoint_data[:plot_length], 'b-', 
             label='Setpoint', linewidth=2)
    plt.plot(time_data[:plot_length], gyro_data[:plot_length], 'r-', 
             label='Gyro Response', linewidth=2)
    
    # Calculate and plot error
    error = setpoint_data[:plot_length] - gyro_data[:plot_length]
    plt.plot(time_data[:plot_length], error, 'g-', 
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
    if max(abs(error)) > 15:
        peak_error_idx = np.argmax(abs(error[:plot_length]))
        plt.annotate('Peak Error', 
                    xy=(time_data[peak_error_idx], error[peak_error_idx]),
                    xytext=(time_data[peak_error_idx], error[peak_error_idx] * 1.2),
                    arrowprops=dict(facecolor='black', shrink=0.05, width=1.5),
                    fontsize=10)
    
    # Save figure and embed in HTML
    plot_path = os.path.join(output_dir, f'{axis}_segment_{segment_id}.png')
    plt.savefig(plot_path, dpi=150, bbox_inches='tight')
    
    # Create base64 version for HTML embedding
    img_base64 = fig_to_base64(fig)
    plt.close(fig)
    
    return img_base64, plot_path

def plot_psd(f, pxx, peak_freq, peak_power, axis, segment_id, output_dir):
    """Create an enhanced PSD plot with oscillation indicators"""
    fig = plt.figure(figsize=(12, 8), dpi=150)
    
    # Use a more visually distinct color scheme
    plt.semilogy(f, pxx, linewidth=2, color='darkblue')
    
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
    psd_path = os.path.join(output_dir, f'{axis}_psd_segment_{segment_id}.png')
    plt.savefig(psd_path, dpi=150, bbox_inches='tight')
    
    # Create base64 version for HTML embedding
    img_base64 = fig_to_base64(fig)
    plt.close(fig)
    
    return img_base64, psd_path

def analyze_flight_characteristics(df, segments, output_dir):
    """
    Analyze flight characteristics for active segments.
    Saves plots to the specified output directory.
    """
    results = {
        'roll': {},
        'pitch': {},
        'yaw': {}
    }
    
    html_content = ""
    
    # Process each segment
    for i, (start, end) in enumerate(segments):
        segment_df = df.iloc[start:end].copy()
        duration = segment_df['time'].iloc[-1] - segment_df['time'].iloc[0]
        
        segment_html = f"<h3>Flight Segment {i+1} (Duration: {duration:.1f}s)</h3>"
        print(f"\nAnalyzing flight segment {i+1} (duration: {duration:.1f}s)")
        
        segment_html += "<div class='segment'>"
        
        # Analyze each axis
        for axis in ['roll', 'pitch', 'yaw']:
            # Extract data
            rc_data = segment_df[f'rc_{axis}'].values
            setpoint_data = segment_df[f'setpoint_{axis}'].values
            gyro_data = segment_df[f'gyro_{axis}'].values
            time_data = segment_df['time'].values
            
            # Basic statistics
            rc_mean = np.mean(rc_data)
            rc_std = np.std(rc_data)
            rc_min = np.min(rc_data)
            rc_max = np.max(rc_data)
            
            sp_mean = np.mean(setpoint_data)
            sp_std = np.std(setpoint_data)
            sp_min = np.min(setpoint_data)
            sp_max = np.max(setpoint_data)
            
            gyro_mean = np.mean(gyro_data)
            gyro_std = np.std(gyro_data)
            gyro_min = np.min(gyro_data)
            gyro_max = np.max(gyro_data)
            
            print(f"\n{axis.upper()} axis:")
            print(f"  RC: mean={rc_mean:.1f}, std={rc_std:.1f}, range=[{rc_min:.1f}, {rc_max:.1f}]")
            print(f"  Setpoint: mean={sp_mean:.1f}, std={sp_std:.1f}, range=[{sp_min:.1f}, {sp_max:.1f}]")
            print(f"  Gyro: mean={gyro_mean:.1f}, std={gyro_std:.1f}, range=[{gyro_min:.1f}, {gyro_max:.1f}]")
            
            # Calculate tracking error
            error = setpoint_data - gyro_data
            error_mean = np.mean(np.abs(error))
            error_rms = np.sqrt(np.mean(np.square(error)))
            error_peak = np.max(np.abs(error))
            
            print(f"  Error metrics: mean={error_mean:.1f}, RMS={error_rms:.1f}, peak={error_peak:.1f}")
            
            # Generate HTML for this axis
            axis_html = f"<div class='axis-data'>"
            axis_html += f"<h4>{axis.upper()} Axis</h4>"
            axis_html += "<table class='stats-table'>"
            axis_html += "<tr><th>Metric</th><th>RC</th><th>Setpoint</th><th>Gyro</th></tr>"
            axis_html += f"<tr><td>Mean</td><td>{rc_mean:.1f}</td><td>{sp_mean:.1f}</td><td>{gyro_mean:.1f}</td></tr>"
            axis_html += f"<tr><td>Std Dev</td><td>{rc_std:.1f}</td><td>{sp_std:.1f}</td><td>{gyro_std:.1f}</td></tr>"
            axis_html += f"<tr><td>Min</td><td>{rc_min:.1f}</td><td>{sp_min:.1f}</td><td>{gyro_min:.1f}</td></tr>"
            axis_html += f"<tr><td>Max</td><td>{rc_max:.1f}</td><td>{sp_max:.1f}</td><td>{gyro_max:.1f}</td></tr>"
            axis_html += "</table>"
            
            axis_html += "<table class='error-table'>"
            axis_html += "<tr><th colspan='3'>Error Metrics</th></tr>"
            axis_html += f"<tr><td>Mean</td><td>{error_mean:.1f}</td></tr>"
            axis_html += f"<tr><td>RMS</td><td>{error_rms:.1f}</td></tr>"
            axis_html += f"<tr><td>Peak</td><td>{error_peak:.1f}</td></tr>"
            axis_html += "</table>"
            
            # Calculate power spectral density for oscillation analysis
            frequency_html = ""
            if len(gyro_data) > 1000:  # Only if we have enough data
                fs = 1 / (time_data[1] - time_data[0])  # Sampling frequency
                f, pxx = signal.welch(gyro_data, fs, nperseg=1024)
                
                # Find dominant frequency and its power
                peak_idx = np.argmax(pxx)
                peak_freq = f[peak_idx]
                peak_power = pxx[peak_idx]
                
                print(f"  Dominant frequency: {peak_freq:.1f}Hz, power: {peak_power:.1f}")
                
                frequency_html = f"<p>Dominant frequency: {peak_freq:.1f}Hz, power: {peak_power:.1f}</p>"
                
                # Store all the results for this axis and segment
                results[axis][i] = {
                    'rc_stats': {'mean': rc_mean, 'std': rc_std, 'min': rc_min, 'max': rc_max},
                    'setpoint_stats': {'mean': sp_mean, 'std': sp_std, 'min': sp_min, 'max': sp_max},
                    'gyro_stats': {'mean': gyro_mean, 'std': gyro_std, 'min': gyro_min, 'max': gyro_max},
                    'error_metrics': {'mean': error_mean, 'rms': error_rms, 'peak': error_peak},
                    'frequency_analysis': {'peak_freq': peak_freq, 'peak_power': peak_power},
                }
            else:
                # Store results without frequency analysis
                results[axis][i] = {
                    'rc_stats': {'mean': rc_mean, 'std': rc_std, 'min': rc_min, 'max': rc_max},
                    'setpoint_stats': {'mean': sp_mean, 'std': sp_std, 'min': sp_min, 'max': sp_max},
                    'gyro_stats': {'mean': gyro_mean, 'std': gyro_std, 'min': gyro_min, 'max': gyro_max},
                    'error_metrics': {'mean': error_mean, 'rms': error_rms, 'peak': error_peak}
                }
            
            axis_html += frequency_html
            
            # Generate enhanced time domain plot
            img_base64, _ = plot_time_domain(
                time_data, setpoint_data, gyro_data, 
                axis, i+1, output_dir, error_rms
            )
            
            axis_html += f"<div class='plot'><h5>Time Domain Response</h5>"
            axis_html += f"<img src='data:image/png;base64,{img_base64}' alt='{axis} response'>"
            axis_html += "<p class='plot-explanation'><b>How to interpret:</b> Blue line shows setpoint (what the drone should do), red line shows gyro (what the drone actually did), and green line shows the error between them. Good tuning shows minimal error and prompt response to setpoint changes.</p>"
            axis_html += "</div>"
            
            # Create enhanced PSD plot if we have enough data
            if len(gyro_data) > 1000:
                img_base64, _ = plot_psd(
                    f, pxx, peak_freq, peak_power,
                    axis, i+1, output_dir
                )
                
                axis_html += f"<div class='plot'><h5>Frequency Domain Analysis</h5>"
                axis_html += f"<img src='data:image/png;base64,{img_base64}' alt='{axis} PSD'>"
                axis_html += "<p class='plot-explanation'><b>How to interpret:</b> This shows frequency content of the gyro signal. Peaks in low frequencies (green) may indicate P too high or I too low. Peaks in mid frequencies (orange) may indicate P tuning issues. Peaks in high frequencies (red) may indicate D too high or noise issues.</p>"
                axis_html += "</div>"
            
            axis_html += "</div>"  # End of axis-data div
            segment_html += axis_html
        
        segment_html += "</div>"  # End of segment div
        html_content += segment_html
    
    return results, html_content

def generate_tuning_recommendations(flight_analysis):
    """
    Generate PID tuning recommendations based on flight analysis.
    """
    # Aggregate results across all segments
    aggregated = {
        'roll': {
            'error_mean': [],
            'error_rms': [],
            'error_peak': [],
            'peak_freq': [],
            'peak_power': []
        },
        'pitch': {
            'error_mean': [],
            'error_rms': [],
            'error_peak': [],
            'peak_freq': [],
            'peak_power': []
        },
        'yaw': {
            'error_mean': [],
            'error_rms': [],
            'error_peak': [],
            'peak_freq': [],
            'peak_power': []
        }
    }
    
    # Collect data from all segments
    for axis in ['roll', 'pitch', 'yaw']:
        for segment_id, data in flight_analysis[axis].items():
            aggregated[axis]['error_mean'].append(data['error_metrics']['mean'])
            aggregated[axis]['error_rms'].append(data['error_metrics']['rms'])
            aggregated[axis]['error_peak'].append(data['error_metrics']['peak'])
            
            if 'frequency_analysis' in data:
                aggregated[axis]['peak_freq'].append(data['frequency_analysis']['peak_freq'])
                aggregated[axis]['peak_power'].append(data['frequency_analysis']['peak_power'])
    
    # Generate recommendations
    recommendations = {}
    html_content = "<h2>PID Tuning Recommendations</h2>"
    
    for axis in ['roll', 'pitch', 'yaw']:
        print(f"\n{axis.upper()} Axis Tuning Recommendations:")
        html_content += f"<div class='axis-recommendations' id='{axis}-recommendations'>"
        html_content += f"<h3>{axis.upper()} Axis Tuning Recommendations</h3>"
        
        # Calculate averages
        avg_error_mean = np.mean(aggregated[axis]['error_mean'])
        avg_error_rms = np.mean(aggregated[axis]['error_rms'])
        avg_error_peak = np.mean(aggregated[axis]['error_peak'])
        
        print(f"Average error metrics: mean={avg_error_mean:.1f}, RMS={avg_error_rms:.1f}, peak={avg_error_peak:.1f}")
        html_content += f"<p>Average error metrics: mean={avg_error_mean:.1f}, RMS={avg_error_rms:.1f}, peak={avg_error_peak:.1f}</p>"
        
        # Initialize recommendations
        p_adjustment = 0
        i_adjustment = 0
        d_adjustment = 0
        
        recommendations_text = []
        
        # P-term recommendations based on tracking error
        if avg_error_rms > 50:
            p_adjustment += 15
            msg = f"High RMS error ({avg_error_rms:.1f}): Consider increasing P by ~15%"
            print(msg)
            recommendations_text.append(msg)
        elif avg_error_rms < 10:
            msg = "Good tracking performance"
            print(msg)
            recommendations_text.append(msg)
        
        # Check for oscillations
        if len(aggregated[axis]['peak_freq']) > 0:
            avg_peak_freq = np.mean(aggregated[axis]['peak_freq'])
            avg_peak_power = np.mean(aggregated[axis]['peak_power'])
            
            print(f"Average dominant frequency: {avg_peak_freq:.1f}Hz, power: {avg_peak_power:.1f}")
            html_content += f"<p>Average dominant frequency: {avg_peak_freq:.1f}Hz, power: {avg_peak_power:.1f}</p>"
            
            # High frequency oscillations often indicate too much D
            if avg_peak_freq > 30 and avg_peak_power > 1000:
                d_adjustment -= 20
                msg = f"High frequency oscillations detected ({avg_peak_freq:.1f}Hz): Consider reducing D by ~20%"
                print(msg)
                recommendations_text.append(msg)
            
            # Low frequency oscillations often indicate too much P or too little D
            elif avg_peak_freq < 10 and avg_peak_power > 1000:
                p_adjustment -= 10
                d_adjustment += 15
                msg = f"Low frequency oscillations detected ({avg_peak_freq:.1f}Hz): Consider reducing P by ~10% and increasing D by ~15%"
                print(msg)
                recommendations_text.append(msg)
            
            # Medium frequency with high power might indicate too much P
            elif 10 <= avg_peak_freq <= 30 and avg_peak_power > 2000:
                p_adjustment -= 10
                msg = f"Medium frequency oscillations detected ({avg_peak_freq:.1f}Hz): Consider reducing P by ~10%"
                print(msg)
                recommendations_text.append(msg)
        
        # I-term recommendations based on persistent error
        if avg_error_mean > 30:
            i_adjustment += 20
            msg = f"High average error ({avg_error_mean:.1f}): Consider increasing I by ~20%"
            print(msg)
            recommendations_text.append(msg)
        
        recommendations[axis] = {
            'P': p_adjustment,
            'I': i_adjustment,
            'D': d_adjustment
        }
        
        print("\nRecommended PID adjustments:")
        print(f"P: {p_adjustment:+d}%")
        print(f"I: {i_adjustment:+d}%")
        print(f"D: {d_adjustment:+d}%")
        
        html_content += "<div class='recommendations'>"
        html_content += "<h4>Specific Recommendations:</h4>"
        if recommendations_text:
            html_content += "<ul>"
            for rec in recommendations_text:
                html_content += f"<li>{rec}</li>"
            html_content += "</ul>"
        else:
            html_content += "<p>No specific issues detected. Current tune appears to be well-balanced.</p>"
        html_content += "</div>"
        
        html_content += "<div class='pid-adjustments'>"
        html_content += "<h4>Recommended PID Adjustments:</h4>"
        html_content += "<table class='pid-table'>"
        html_content += "<tr><th>Term</th><th>Adjustment</th></tr>"
        html_content += f"<tr><td>P</td><td>{p_adjustment:+d}%</td></tr>"
        html_content += f"<tr><td>I</td><td>{i_adjustment:+d}%</td></tr>"
        html_content += f"<tr><td>D</td><td>{d_adjustment:+d}%</td></tr>"
        html_content += "</table>"
        html_content += "</div>"
        
        # Additional advice
        html_content += "<div class='additional-advice'>"
        html_content += "<h4>Additional Notes:</h4>"
        
        if abs(p_adjustment) < 5 and abs(i_adjustment) < 5 and abs(d_adjustment) < 5:
            msg = "Current tune appears to be well-balanced."
            print(msg)
            html_content += f"<p>{msg}</p>"
        
        if avg_error_peak > 100:
            msg = "High peak errors detected. This could indicate mechanical issues or extreme maneuvers."
            print(msg)
            html_content += f"<p>{msg}</p>"
            
        html_content += "</div>"  # End of additional-advice div
        html_content += "</div>"  # End of axis-recommendations div
    
    return recommendations, html_content

def generate_html_report(file_path, results, segments_html, recommendations_html):
    """
    Generate an HTML report for the analysis.
    """
    log_name = os.path.basename(file_path)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Betaflight Log Analysis - {log_name}</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 20px;
                color: #333;
                line-height: 1.6;
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
            }}
            header {{
                background-color: #2c3e50;
                color: white;
                padding: 20px;
                margin-bottom: 20px;
                border-radius: 5px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }}
            h1, h2, h3, h4, h5 {{
                color: #2c3e50;
                margin-top: 20px;
            }}
            header h1, header h2, header h3 {{
                color: white;
                margin: 5px 0;
            }}
            .summary {{
                background-color: #f8f9fa;
                padding: 15px;
                border-radius: 5px;
                margin-bottom: 20px;
                border-left: 5px solid #2c3e50;
            }}
            .segment {{
                background-color: #fff;
                padding: 15px;
                margin-bottom: 30px;
                border-radius: 5px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }}
            .axis-data {{
                border-top: 1px solid #ddd;
                padding-top: 15px;
                margin-top: 15px;
            }}
            table {{
                border-collapse: collapse;
                margin: 15px 0;
                width: 100%;
            }}
            th, td {{
                border: 1px solid #ddd;
                padding: 8px 12px;
                text-align: left;
            }}
            th {{
                background-color: #f2f2f2;
            }}
            .stats-table, .error-table, .pid-table {{
                width: auto;
                min-width: 300px;
            }}
            .plot {{
                margin: 20px 0;
            }}
            .plot img {{
                max-width: 100%;
                height: auto;
                border: 1px solid #ddd;
                border-radius: 3px;
            }}
            .plot-explanation {{
                font-size: 0.9em;
                color: #555;
                margin-top: 5px;
                padding: 10px;
                background-color: #f9f9f9;
                border-left: 3px solid #2c3e50;
            }}
            .axis-recommendations {{
                background-color: #f8f9fa;
                padding: 15px;
                margin: 20px 0;
                border-radius: 5px;
                border-left: 5px solid #27ae60;
            }}
            .recommendations ul {{
                padding-left: 20px;
            }}
            .nav {{
                position: sticky;
                top: 0;
                background-color: #2c3e50;
                padding: 10px 20px;
                margin-bottom: 20px;
                border-radius: 5px;
                display: flex;
                overflow-x: auto;
                white-space: nowrap;
            }}
            .nav a {{
                color: white;
                text-decoration: none;
                margin-right: 15px;
                padding: 5px 10px;
                border-radius: 3px;
            }}
            .nav a:hover {{
                background-color: rgba(255,255,255,0.1);
            }}
            .clearfix::after {{
                content: "";
                clear: both;
                display: table;
            }}
            @media (max-width: 768px) {{
                .nav {{
                    flex-direction: column;
                }}
                .nav a {{
                    margin-bottom: 5px;
                }}
            }}
            .footer {{
                text-align: center;
                margin-top: 40px;
                padding-top: 20px;
                border-top: 1px solid #ddd;
                color: #777;
                font-size: 0.9em;
            }}
            .tuning-guide-section {{
                background-color: #f0f7ff;
                padding: 15px;
                margin: 20px 0;
                border-radius: 5px;
                border-left: 5px solid #3498db;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>Betaflight Log Analysis</h1>
                <h2>{log_name}</h2>
                <h3>Analysis Date: {timestamp}</h3>
            </header>
            
            <div class="nav">
                <a href="#summary">Summary</a>
                <a href="#tuning-guide">Tuning Guide</a>
                <a href="#recommendations">Recommendations</a>
                <a href="#segments">Flight Segments</a>
                <a href="#roll-recommendations">Roll</a>
                <a href="#pitch-recommendations">Pitch</a>
                <a href="#yaw-recommendations">Yaw</a>
            </div>
            
            <div class="summary" id="summary">
                <h2>Analysis Summary</h2>
                <p>This report analyzes the flight characteristics and PID tuning of your Betaflight-powered drone based on the log file.</p>
                <p>The analysis examines tracking performance, oscillations, and overall flight behavior to provide recommendations for PID tuning.</p>
                <p>Found {len(results['roll'])} flight segments for analysis.</p>
            </div>
            
            <div class="tuning-guide-section" id="tuning-guide">
                <h2>How to Interpret PID Tuning Graphs</h2>
                
                <h3>Time Domain Graphs</h3>
                <p>These graphs show how your drone responds to control inputs over time:</p>
                <ul>
                    <li><strong>Blue line</strong>: Setpoint - What your drone is trying to do (the target)</li>
                    <li><strong>Red line</strong>: Gyro - What your drone actually did (the response)</li>
                    <li><strong>Green line</strong>: Error - The difference between setpoint and gyro</li>
                </ul>
                
                <h4>What Good Tuning Looks Like:</h4>
                <ul>
                    <li>Red line closely follows blue line with minimal delay</li>
                    <li>Small, consistent error (green line stays close to zero)</li>
                    <li>No oscillations after changes in setpoint</li>
                    <li>RMS error below 10 indicates excellent tracking</li>
                </ul>
                
                <h4>Common PID Tuning Issues:</h4>
                <ul>
                    <li><strong>P too low</strong>: Slow response, large gap between setpoint and gyro</li>
                    <li><strong>P too high</strong>: Overshoot followed by oscillations</li>
                    <li><strong>I too low</strong>: Drone doesn't reach target, persistent error</li>
                    <li><strong>I too high</strong>: Slow oscillations that take time to settle</li>
                    <li><strong>D too low</strong>: Overshoot and oscillations when changing direction</li>
                    <li><strong>D too high</strong>: High-frequency vibrations, especially during rapid moves</li>
                </ul>
                
                <h3>Frequency Domain Graphs</h3>
                <p>These graphs show the frequency content of your drone's motion:</p>
                <ul>
                    <li><strong>Green area (0-10Hz)</strong>: Low frequency content - often related to P and I term issues</li>
                    <li><strong>Orange area (10-30Hz)</strong>: Mid frequency content - often related to P term and motor response</li>
                    <li><strong>Red area (>30Hz)</strong>: High frequency content - often related to D term and mechanical issues</li>
                </ul>
                
                <p>A well-tuned drone typically shows a smooth curve with no sharp peaks, especially in the mid and high frequency ranges.</p>
            </div>
            
            <div id="recommendations">
                {recommendations_html}
            </div>
            
            <h2 id="segments">Flight Segments Analysis</h2>
            {segments_html}
            
            <div class="footer">
                <p>Generated by Betaflight PID Analyzer</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html

def main():
    """
    Main function to run the analysis.
    """
    # Check if a file path is provided
    if len(sys.argv) < 2:
        print("Usage: python pid_analyzer.py <log_file>")
        return
    
    # Get the file path
    file_path = sys.argv[1]
    print(f"Analyzing blackbox log: {file_path}")
    
    # Create output directory based on log file name
    log_name = os.path.basename(file_path)
    base_name = os.path.splitext(log_name)[0]
    output_dir = os.path.join(os.path.dirname(file_path), f"{base_name}_analysis")
    os.makedirs(output_dir, exist_ok=True)
    
    # Read the log file
    df = read_blackbox_log(file_path)
    if df is None:
        return
    
    # Print some basic information
    print("\nFirst few rows of the data:")
    print(df.head())
    
    print("\nColumns in the data:")
    print(df.columns.tolist())
    
    # Identify flight segments
    segments = identify_flight_segments(df)
    
    # Analyze flight characteristics
    analysis, segments_html = analyze_flight_characteristics(df, segments, output_dir)
    
    # Generate tuning recommendations
    recommendations, recommendations_html = generate_tuning_recommendations(analysis)
    
    # Generate HTML report
    html_report = generate_html_report(file_path, analysis, segments_html, recommendations_html)
    
    # Save HTML report
    report_path = os.path.join(output_dir, f"{base_name}_report.html")
    with open(report_path, 'w') as f:
        f.write(html_report)
    
    print(f"\nAnalysis complete. HTML report saved to: {report_path}")
    print(f"All analysis files saved to: {output_dir}")

if __name__ == "__main__":
    main() 