"""
Main entry point for the Betaflight Log Analyzer
"""
import os
import sys
import argparse

from betaflight_log_analyzer.utils.log_reader import BlackboxLogReader
from betaflight_log_analyzer.analysis.segment_analyzer import FlightSegmentAnalyzer
from betaflight_log_analyzer.analysis.pid_recommender import PIDRecommender
from betaflight_log_analyzer.visualization.plots import PlotGenerator
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
    
    # Generate plots and analyze segments
    plot_generator = PlotGenerator(args.output_dir)
    segment_results = {}
    segment_plots = {}
    
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
    
    # Generate PID recommendations
    pid_recommender = PIDRecommender()
    recommendations, recommendations_text = pid_recommender.generate_recommendations(segment_results)
    
    # Generate HTML report
    html_reporter = HTMLReporter(args.output_dir, args.log_file)
    report_path = html_reporter.generate_report(
        segment_results, recommendations, recommendations_text, segment_plots
    )
    
    print(f"\nAnalysis complete. HTML report saved to: {report_path}")
    print(f"All analysis files saved to: {args.output_dir}")

if __name__ == "__main__":
    main() 