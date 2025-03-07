"""
Main entry point for the Betaflight Log Analyzer
"""
import os
import sys
import argparse

from betaflight_log_analyzer.utils.log_reader import BlackboxLogReader
from betaflight_log_analyzer.analysis.segment_analyzer import FlightSegmentAnalyzer
from betaflight_log_analyzer.analysis.pid_recommender import PIDRecommender
from betaflight_log_analyzer.analysis.advanced_analysis import AdvancedAnalyzer
from betaflight_log_analyzer.visualization.plots import PlotGenerator
from betaflight_log_analyzer.visualization.advanced_plots import AdvancedPlotGenerator
from betaflight_log_analyzer.reports.html_reporter import HTMLReporter

def main():
    """
    Main function to run the analysis.
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Analyze Betaflight blackbox logs and provide PID tuning recommendations'
    )
    parser.add_argument('log_file', help='Path to the blackbox log file')
    parser.add_argument(
        '--blackbox-decode', 
        help='Path to the blackbox_decode executable'
    )
    parser.add_argument(
        '--throttle-threshold', 
        type=int, 
        default=1300,
        help='Throttle value above which flight is considered active'
    )
    parser.add_argument(
        '--output-dir', 
        help='Directory to save report and plots (defaults to log file directory)'
    )
    parser.add_argument(
        '--advanced', 
        action='store_true',
        help='Enable advanced analysis techniques'
    )
    parser.add_argument(
        '--skip-wavelet', 
        action='store_true',
        help='Skip wavelet analysis (can be computationally intensive)'
    )
    
    args = parser.parse_args()
    
    # Set default output directory if not specified
    if not args.output_dir:
        log_name = os.path.basename(args.log_file)
        base_name = os.path.splitext(log_name)[0]
        args.output_dir = os.path.join(os.path.dirname(args.log_file), f"{base_name}_analysis")
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    print(f"Analyzing blackbox log: {args.log_file}")
    
    # Read the log file
    log_reader = BlackboxLogReader(args.blackbox_decode)
    df = log_reader.read_log(args.log_file)
    if df is None:
        return
    
    # Print some basic information
    print("\nFirst few rows of the data:")
    print(df.head())
    
    print("\nColumns in the data:")
    print(df.columns.tolist())
    
    # Analyze flight segments
    segment_analyzer = FlightSegmentAnalyzer(args.throttle_threshold)
    segments = segment_analyzer.identify_segments(df)
    
    # Initialize advanced analyzer if requested
    advanced_analyzer = None
    if args.advanced:
        print("\nPerforming advanced analysis...")
        advanced_analyzer = AdvancedAnalyzer()
    
    # Generate plots and analyze segments
    plot_generator = PlotGenerator(args.output_dir)
    advanced_plot_generator = None
    if args.advanced:
        advanced_plot_generator = AdvancedPlotGenerator(args.output_dir)
    
    segment_results = {}
    segment_plots = {}
    advanced_results = {}
    advanced_plots = {}
    
    for i, segment in enumerate(segments):
        # Analyze segment
        segment_data = segment_analyzer.analyze_segment(df, segment)
        segment_results[i] = segment_data
        
        # Generate plots for each axis
        for axis in ['roll', 'pitch', 'yaw']:
            if axis in segment_data:
                axis_data = segment_data[axis]
                
                # Generate time domain plot
                time_domain_img, _ = plot_generator.plot_time_domain(
                    axis_data['time'],
                    axis_data['setpoint'],
                    axis_data['gyro'],
                    axis_data['error'],
                    axis,
                    i+1,
                    axis_data['error_metrics']['rms']
                )
                
                # Generate PSD plot if frequency analysis available
                psd_img = None
                if 'frequency_analysis' in axis_data:
                    psd_img, _ = plot_generator.plot_psd(
                        axis_data['frequency_analysis']['frequencies'],
                        axis_data['frequency_analysis']['power'],
                        axis_data['frequency_analysis']['peak_freq'],
                        axis_data['frequency_analysis']['peak_power'],
                        axis,
                        i+1
                    )
                    
                    segment_plots[f"{i}_{axis}"] = {
                        'time_domain': time_domain_img,
                        'psd': psd_img
                    }
                else:
                    segment_plots[f"{i}_{axis}"] = {
                        'time_domain': time_domain_img
                    }
                
                # Perform advanced analysis if requested
                if args.advanced:
                    plot_key = f"{i}_{axis}"
                    advanced_plots[plot_key] = {}
                    advanced_results[plot_key] = {}
                    
                    # Extract relevant data for analysis
                    time_data = axis_data['time']
                    setpoint_data = axis_data['setpoint']
                    gyro_data = axis_data['gyro']
                    
                    # 1. Transfer function estimation
                    print(f"\nEstimating transfer function for {axis} axis, segment {i+1}...")
                    tf_data = advanced_analyzer.estimate_transfer_function(
                        time_data, setpoint_data, gyro_data
                    )
                    advanced_results[plot_key]['transfer_function'] = tf_data
                    
                    # Generate transfer function plot
                    tf_img, _ = advanced_plot_generator.plot_transfer_function(
                        tf_data, axis, i+1
                    )
                    advanced_plots[plot_key]['transfer_function'] = tf_img
                    
                    # 2. ARX model identification
                    print(f"Identifying ARX model for {axis} axis, segment {i+1}...")
                    arx_data = advanced_analyzer.identify_arx_model(
                        time_data, setpoint_data, gyro_data
                    )
                    advanced_results[plot_key]['arx_model'] = arx_data
                    
                    # Generate ARX model plot
                    arx_img, _ = advanced_plot_generator.plot_arx_model(
                        arx_data, time_data, setpoint_data, gyro_data, axis, i+1
                    )
                    advanced_plots[plot_key]['arx_model'] = arx_img
                    
                    # 3. Wavelet analysis (if not skipped)
                    if not args.skip_wavelet:
                        print(f"Performing wavelet analysis for {axis} axis, segment {i+1}...")
                        wavelet_data = advanced_analyzer.wavelet_analysis(
                            time_data, gyro_data
                        )
                        if wavelet_data is not None:
                            advanced_results[plot_key]['wavelet'] = wavelet_data
                            
                            # Generate wavelet plot
                            wavelet_img, _ = advanced_plot_generator.plot_wavelet_analysis(
                                wavelet_data, axis, i+1
                            )
                            advanced_plots[plot_key]['wavelet'] = wavelet_img
                    
                    # 4. Performance index
                    print(f"Calculating performance index for {axis} axis, segment {i+1}...")
                    perf_data = advanced_analyzer.calculate_performance_index(
                        time_data, setpoint_data, gyro_data
                    )
                    advanced_results[plot_key]['performance'] = perf_data
                    
                    # Generate performance plot
                    perf_img, _ = advanced_plot_generator.plot_performance_index(
                        perf_data, axis, i+1
                    )
                    advanced_plots[plot_key]['performance'] = perf_img
    
    # Generate PID recommendations
    pid_recommender = PIDRecommender()
    recommendations, recommendations_text = pid_recommender.generate_recommendations(
        segment_results, 
        advanced_results=advanced_results if args.advanced else None
    )
    
    # Generate HTML report
    html_reporter = HTMLReporter(args.output_dir, args.log_file)
    report_path = html_reporter.generate_report(
        segment_results, recommendations, recommendations_text, segment_plots,
        advanced_results=advanced_results if args.advanced else None,
        advanced_plots=advanced_plots if args.advanced else None
    )
    
    print(f"\nAnalysis complete. HTML report saved to: {report_path}")
    print(f"All analysis files saved to: {args.output_dir}")

if __name__ == "__main__":
    main() 