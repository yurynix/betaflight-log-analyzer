"""
Module for generating HTML reports from analysis results
"""
import os
import datetime

class HTMLReporter:
    """Class for generating HTML reports"""
    
    def __init__(self, output_dir, log_file_path):
        """
        Initialize the HTML reporter
        
        Args:
            output_dir: Directory to save report to
            log_file_path: Path to the original log file
        """
        self.output_dir = output_dir
        self.log_file_path = log_file_path
        self.log_name = os.path.basename(log_file_path)
    
    def generate_report(self, analysis_results, recommendations, recommendations_text, segment_plots):
        """
        Generate an HTML report from analysis results
        
        Args:
            analysis_results: Dictionary with analysis results for each segment and axis
            recommendations: Dictionary with PID recommendations for each axis
            recommendations_text: Dictionary with recommendation text for each axis
            segment_plots: Dictionary with plot data for each segment and axis
            
        Returns:
            Path to the generated HTML report
        """
        # Create HTML report
        html = self._generate_html_content(analysis_results, recommendations, 
                                          recommendations_text, segment_plots)
        
        # Save the HTML report
        report_path = os.path.join(self.output_dir, 
                                   f"{os.path.splitext(self.log_name)[0]}_report.html")
        with open(report_path, 'w') as f:
            f.write(html)
        
        return report_path
    
    def _generate_html_content(self, analysis_results, recommendations, recommendations_text, segment_plots):
        """
        Generate the HTML content for the report
        
        Args:
            analysis_results: Dictionary with analysis results for each segment and axis
            recommendations: Dictionary with PID recommendations for each axis
            recommendations_text: Dictionary with recommendation text for each axis
            segment_plots: Dictionary with plot data for each segment and axis
            
        Returns:
            HTML content as a string
        """
        # Get timestamp for the report
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Create the HTML content
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Betaflight Log Analysis - {self.log_name}</title>
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
                    <h2>{self.log_name}</h2>
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
                    <p>Found {len(analysis_results)} flight segments for analysis.</p>
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
                    <h2>PID Tuning Recommendations</h2>
        """
        
        # Add recommendations for each axis
        for axis in ['roll', 'pitch', 'yaw']:
            if axis in recommendations:
                rec = recommendations[axis]
                html += f"""
                    <div class="axis-recommendations" id="{axis}-recommendations">
                        <h3>{axis.upper()} Axis Tuning Recommendations</h3>
                        
                        <p>Average error metrics: 
                           mean={rec['error_metrics']['mean']:.1f}, 
                           RMS={rec['error_metrics']['rms']:.1f}, 
                           peak={rec['error_metrics']['peak']:.1f}
                        </p>
                """
                
                # Add frequency information if available
                if 'frequency' in rec:
                    html += f"""
                        <p>Average dominant frequency: 
                           {rec['frequency']['peak_freq']:.1f}Hz, 
                           power: {rec['frequency']['peak_power']:.1f}
                        </p>
                    """
                
                # Add specific recommendations
                html += """
                        <div class="recommendations">
                            <h4>Specific Recommendations:</h4>
                """
                
                if recommendations_text[axis]:
                    html += "<ul>"
                    for text in recommendations_text[axis]:
                        html += f"<li>{text}</li>"
                    html += "</ul>"
                else:
                    html += "<p>No specific issues detected. Current tune appears to be well-balanced.</p>"
                
                html += """
                        </div>
                        
                        <div class="pid-adjustments">
                            <h4>Recommended PID Adjustments:</h4>
                            <table class="pid-table">
                                <tr><th>Term</th><th>Adjustment</th></tr>
                """
                
                html += f"""
                                <tr><td>P</td><td>{rec['P']:+d}%</td></tr>
                                <tr><td>I</td><td>{rec['I']:+d}%</td></tr>
                                <tr><td>D</td><td>{rec['D']:+d}%</td></tr>
                            </table>
                        </div>
                    </div>
                """
        
        # Add segment analysis
        html += """
                <h2 id="segments">Flight Segments Analysis</h2>
        """
        
        # Add each segment
        for segment_id, segment_data in analysis_results.items():
            first_axis_data = next(iter(segment_data.values()))
            duration = first_axis_data['duration']
            
            html += f"""
                <h3>Flight Segment {segment_id+1} (Duration: {duration:.1f}s)</h3>
                <div class="segment">
            """
            
            # Add data for each axis
            for axis in ['roll', 'pitch', 'yaw']:
                if axis in segment_data:
                    axis_data = segment_data[axis]
                    
                    html += f"""
                        <div class="axis-data">
                            <h4>{axis.upper()} Axis</h4>
                            
                            <table class="stats-table">
                                <tr><th>Metric</th><th>RC</th><th>Setpoint</th><th>Gyro</th></tr>
                                <tr>
                                    <td>Mean</td>
                                    <td>{axis_data['rc_stats']['mean']:.1f}</td>
                                    <td>{axis_data['setpoint_stats']['mean']:.1f}</td>
                                    <td>{axis_data['gyro_stats']['mean']:.1f}</td>
                                </tr>
                                <tr>
                                    <td>Std Dev</td>
                                    <td>{axis_data['rc_stats']['std']:.1f}</td>
                                    <td>{axis_data['setpoint_stats']['std']:.1f}</td>
                                    <td>{axis_data['gyro_stats']['std']:.1f}</td>
                                </tr>
                                <tr>
                                    <td>Min</td>
                                    <td>{axis_data['rc_stats']['min']:.1f}</td>
                                    <td>{axis_data['setpoint_stats']['min']:.1f}</td>
                                    <td>{axis_data['gyro_stats']['min']:.1f}</td>
                                </tr>
                                <tr>
                                    <td>Max</td>
                                    <td>{axis_data['rc_stats']['max']:.1f}</td>
                                    <td>{axis_data['setpoint_stats']['max']:.1f}</td>
                                    <td>{axis_data['gyro_stats']['max']:.1f}</td>
                                </tr>
                            </table>
                            
                            <table class="error-table">
                                <tr><th colspan="2">Error Metrics</th></tr>
                                <tr><td>Mean</td><td>{axis_data['error_metrics']['mean']:.1f}</td></tr>
                                <tr><td>RMS</td><td>{axis_data['error_metrics']['rms']:.1f}</td></tr>
                                <tr><td>Peak</td><td>{axis_data['error_metrics']['peak']:.1f}</td></tr>
                            </table>
                    """
                    
                    # Add frequency information if available
                    if 'frequency_analysis' in axis_data:
                        html += f"""
                            <p>Dominant frequency: 
                               {axis_data['frequency_analysis']['peak_freq']:.1f}Hz, 
                               power: {axis_data['frequency_analysis']['peak_power']:.1f}
                            </p>
                        """
                    
                    # Add plots if available
                    plot_key = f"{segment_id}_{axis}"
                    if plot_key in segment_plots and 'time_domain' in segment_plots[plot_key]:
                        html += f"""
                            <div class="plot">
                                <h5>Time Domain Response</h5>
                                <img src="data:image/png;base64,{segment_plots[plot_key]['time_domain']}" alt="{axis} response">
                                <p class="plot-explanation"><b>How to interpret:</b> Blue line shows setpoint (what the drone should do), red line shows gyro (what the drone actually did), and green line shows the error between them. Good tuning shows minimal error and prompt response to setpoint changes.</p>
                            </div>
                        """
                    
                    if plot_key in segment_plots and 'psd' in segment_plots[plot_key]:
                        html += f"""
                            <div class="plot">
                                <h5>Frequency Domain Analysis</h5>
                                <img src="data:image/png;base64,{segment_plots[plot_key]['psd']}" alt="{axis} PSD">
                                <p class="plot-explanation"><b>How to interpret:</b> This shows frequency content of the gyro signal. Peaks in low frequencies (green) may indicate P too high or I too low. Peaks in mid frequencies (orange) may indicate P tuning issues. Peaks in high frequencies (red) may indicate D too high or noise issues.</p>
                            </div>
                        """
                    
                    html += """
                        </div>
                    """
            
            html += """
                </div>
            """
        
        # Finish the HTML
        html += """
                <div class="footer">
                    <p>Generated by Betaflight PID Analyzer</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html 