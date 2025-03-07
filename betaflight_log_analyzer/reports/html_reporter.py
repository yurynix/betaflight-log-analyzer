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
    
    def generate_report(self, analysis_results, recommendations, recommendations_text, segment_plots,
                     advanced_results=None, advanced_plots=None):
        """
        Generate an HTML report from analysis results
        
        Args:
            analysis_results: Dictionary with analysis results for each segment and axis
            recommendations: Dictionary with PID recommendations for each axis
            recommendations_text: Dictionary with recommendation text for each axis
            segment_plots: Dictionary with plot data for each segment and axis
            advanced_results: Optional dictionary with advanced analysis results
            advanced_plots: Optional dictionary with advanced analysis plots
            
        Returns:
            Path to the generated HTML report
        """
        # Create HTML report
        html = self._generate_html_content(
            analysis_results, recommendations, recommendations_text, segment_plots,
            advanced_results, advanced_plots
        )
        
        # Save the HTML report
        report_path = os.path.join(self.output_dir, 
                                   f"{os.path.splitext(self.log_name)[0]}_report.html")
        with open(report_path, 'w') as f:
            f.write(html)
        
        return report_path
    
    def _generate_html_content(self, analysis_results, recommendations, recommendations_text, segment_plots,
                     advanced_results=None, advanced_plots=None):
        """
        Generate the HTML content for the report
        
        Args:
            analysis_results: Dictionary with analysis results for each segment and axis
            recommendations: Dictionary with PID recommendations for each axis
            recommendations_text: Dictionary with recommendation text for each axis
            segment_plots: Dictionary with plot data for each segment and axis
            advanced_results: Optional dictionary with advanced analysis results
            advanced_plots: Optional dictionary with advanced analysis plots
            
        Returns:
            HTML content as a string
        """
        # Get timestamp for the report
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Check if advanced analysis is available
        has_advanced = advanced_results is not None and advanced_plots is not None
        
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
                .advanced-analysis {{
                    background-color: #fff8f0;
                    padding: 15px;
                    margin: 20px 0;
                    border-radius: 5px;
                    border-left: 5px solid #e67e22;
                }}
                .tabs {{
                    margin-top: 20px;
                    overflow: hidden;
                    border: 1px solid #ccc;
                    background-color: #f1f1f1;
                    border-radius: 5px 5px 0 0;
                }}
                .tab-button {{
                    background-color: inherit;
                    float: left;
                    border: none;
                    outline: none;
                    cursor: pointer;
                    padding: 10px 16px;
                    transition: 0.3s;
                    font-size: 16px;
                }}
                .tab-button:hover {{
                    background-color: #ddd;
                }}
                .tab-button.active {{
                    background-color: #3498db;
                    color: white;
                }}
                .tab-content {{
                    display: none;
                    padding: 15px;
                    border: 1px solid #ccc;
                    border-top: none;
                    border-radius: 0 0 5px 5px;
                    animation: fadeEffect 1s;
                }}
                @keyframes fadeEffect {{
                    from {{opacity: 0;}}
                    to {{opacity: 1;}}
                }}
            </style>
            <script>
                function openTab(evt, tabName) {{
                    var i, tabcontent, tabbuttons;
                    tabcontent = document.getElementsByClassName("tab-content");
                    for (i = 0; i < tabcontent.length; i++) {{
                        tabcontent[i].style.display = "none";
                    }}
                    tabbuttons = document.getElementsByClassName("tab-button");
                    for (i = 0; i < tabbuttons.length; i++) {{
                        tabbuttons[i].className = tabbuttons[i].className.replace(" active", "");
                    }}
                    document.getElementById(tabName).style.display = "block";
                    evt.currentTarget.className += " active";
                }}
                
                // Function to open the default tab when page loads
                document.addEventListener('DOMContentLoaded', function() {{
                    // Get the first tab button and click it
                    document.getElementsByClassName('tab-button')[0].click();
                }});
            </script>
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
        """
        
        # Add advanced analysis tab if available
        if has_advanced:
            html += '<a href="#advanced">Advanced Analysis</a>'
        
        # Add axis-specific links
        html += """
                    <a href="#roll-recommendations">Roll</a>
                    <a href="#pitch-recommendations">Pitch</a>
                    <a href="#yaw-recommendations">Yaw</a>
                </div>
                
                <div class="summary" id="summary">
                    <h2>Analysis Summary</h2>
                    <p>This report analyzes the flight characteristics and PID tuning of your Betaflight-powered drone based on the log file.</p>
                    <p>The analysis examines tracking performance, oscillations, and overall flight behavior to provide recommendations for PID tuning.</p>
        """
        
        # Add info about advanced analysis if available
        if has_advanced:
            html += """
                    <p><strong>Advanced Analysis Enabled:</strong> This report includes additional in-depth analysis techniques:</p>
                    <ul>
                        <li><strong>Transfer Function Estimation:</strong> Shows frequency response characteristics</li>
                        <li><strong>ARX Model Identification:</strong> Creates a mathematical model of your drone's behavior</li>
                        <li><strong>Wavelet Analysis:</strong> Detects time-varying oscillations across different frequency bands</li>
                        <li><strong>Performance Index:</strong> Provides comprehensive performance metrics</li>
                    </ul>
            """
            
        html += f"""
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
        """
        
        # Add advanced analysis guide if available
        if has_advanced:
            html += """
                <div class="advanced-analysis" id="advanced-guide">
                    <h2>Understanding Advanced Analysis</h2>
                    
                    <h3>Transfer Function Analysis</h3>
                    <p>The transfer function describes how your drone responds to control inputs in the frequency domain:</p>
                    <ul>
                        <li><strong>Magnitude plot</strong>: Shows how much the drone amplifies or attenuates inputs at different frequencies</li>
                        <li><strong>Phase plot</strong>: Shows the time delay between input and output at different frequencies</li>
                        <li><strong>Coherence plot</strong>: Measures how linearly related the input and output are (values close to 1 are good)</li>
                    </ul>
                    <p>Key indicators of good tuning:</p>
                    <ul>
                        <li>Smooth roll-off in magnitude plot (no sharp peaks)</li>
                        <li>Phase margin > 45° at gain crossover (where magnitude = 0dB)</li>
                        <li>High coherence (>0.8) across flying frequencies (0-20Hz)</li>
                    </ul>
                    
                    <h3>ARX Model Analysis</h3>
                    <p>ARX (AutoRegressive with eXogenous input) models mathematically represent your drone's dynamics:</p>
                    <ul>
                        <li><strong>Model prediction</strong>: Shows how well the mathematical model matches actual flight data</li>
                        <li><strong>Step response</strong>: Shows how the model predicts your drone would respond to a perfect step input</li>
                        <li><strong>Fit percentage</strong>: Measures how accurately the model represents your drone's behavior</li>
                    </ul>
                    
                    <h3>Wavelet Analysis</h3>
                    <p>Wavelet analysis detects oscillations that change over time:</p>
                    <ul>
                        <li><strong>Scalogram</strong>: Heat map showing power at different frequencies over time</li>
                        <li><strong>Dominant frequency</strong>: Tracks the most prominent frequency at each moment</li>
                        <li><strong>Colored regions</strong>: Highlights times when low (green), mid (yellow), or high (red) frequency oscillations occur</li>
                    </ul>
                    
                    <h3>Performance Index</h3>
                    <p>The performance index provides comprehensive metrics on your drone's handling:</p>
                    <ul>
                        <li><strong>Tracking score</strong>: How well the gyro follows the setpoint</li>
                        <li><strong>Noise reduction</strong>: How well high-frequency noise is suppressed</li>
                        <li><strong>Responsiveness</strong>: How quickly the system responds to inputs</li>
                        <li><strong>Overall score</strong>: Weighted combination of all metrics</li>
                    </ul>
                </div>
            """
        
        # Add PID recommendations
        html += """
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
                
                # Add advanced metrics if available
                if 'advanced_metrics' in rec:
                    adv = rec['advanced_metrics']
                    html += """
                        <div class="advanced-metrics">
                            <h4>Advanced Control Metrics:</h4>
                            <table class="metrics-table">
                                <tr><th>Metric</th><th>Value</th><th>Interpretation</th></tr>
                    """
                    
                    if 'phase_margin' in adv:
                        pm = adv['phase_margin']
                        if pm < 30:
                            interp = "Very low (stability risk)"
                            color = "red"
                        elif pm < 45:
                            interp = "Low (marginally stable)"
                            color = "orange"
                        elif pm <= 75:
                            interp = "Good (well balanced)"
                            color = "green"
                        else:
                            interp = "High (sluggish response)"
                            color = "orange"
                            
                        html += f"""
                            <tr>
                                <td>Phase Margin</td>
                                <td>{pm:.1f}°</td>
                                <td style="color:{color}">{interp}</td>
                            </tr>
                        """
                    
                    if 'crossover_freq' in adv:
                        cf = adv['crossover_freq']
                        if cf < 5:
                            interp = "Low (slow response)"
                            color = "orange"
                        elif cf <= 25:
                            interp = "Good (responsive but stable)"
                            color = "green"
                        else:
                            interp = "High (potential instability)"
                            color = "red"
                            
                        html += f"""
                            <tr>
                                <td>Bandwidth</td>
                                <td>{cf:.1f}Hz</td>
                                <td style="color:{color}">{interp}</td>
                            </tr>
                        """
                    
                    if 'rise_time' in adv:
                        rt = adv['rise_time']
                        if rt < 0.05:
                            interp = "Very fast (potential overshoot)"
                            color = "orange"
                        elif rt <= 0.2:
                            interp = "Good (responsive)"
                            color = "green"
                        else:
                            interp = "Slow (sluggish response)"
                            color = "orange"
                            
                        html += f"""
                            <tr>
                                <td>Rise Time</td>
                                <td>{rt:.3f}s</td>
                                <td style="color:{color}">{interp}</td>
                            </tr>
                        """
                    
                    if 'overshoot' in adv:
                        os = adv['overshoot']
                        if os < 5:
                            interp = "Very low (overdamped)"
                            color = "orange"
                        elif os <= 20:
                            interp = "Good (well damped)"
                            color = "green"
                        else:
                            interp = "High (underdamped)"
                            color = "red"
                            
                        html += f"""
                            <tr>
                                <td>Overshoot</td>
                                <td>{os:.1f}%</td>
                                <td style="color:{color}">{interp}</td>
                            </tr>
                        """
                    
                    if 'settling_time' in adv:
                        st = adv['settling_time']
                        if st < 0.3:
                            interp = "Fast (well tuned)"
                            color = "green"
                        elif st <= 0.5:
                            interp = "Good (acceptable)"
                            color = "green"
                        else:
                            interp = "Slow (needs improvement)"
                            color = "orange"
                            
                        html += f"""
                            <tr>
                                <td>Settling Time</td>
                                <td>{st:.3f}s</td>
                                <td style="color:{color}">{interp}</td>
                            </tr>
                        """
                    
                    if 'arx_fit' in adv:
                        fit = adv['arx_fit']
                        if fit < 50:
                            interp = "Poor (non-linear behavior)"
                            color = "red"
                        elif fit <= 70:
                            interp = "Fair (some non-linearities)"
                            color = "orange"
                        else:
                            interp = "Good (linear behavior)"
                            color = "green"
                            
                        html += f"""
                            <tr>
                                <td>System Linearity</td>
                                <td>{fit:.1f}%</td>
                                <td style="color:{color}">{interp}</td>
                            </tr>
                        """
                    
                    html += """
                            </table>
                            <p><em>These metrics are based on advanced control theory analysis of your drone's behavior.</em></p>
                        </div>
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
        
        # Add advanced analysis section if available
        if has_advanced:
            html += """
                <div id="advanced">
                    <h2>Advanced Analysis</h2>
                    <p>This section contains in-depth analysis of your drone's flight characteristics using advanced signal processing techniques.</p>
            """
            
            # Add each segment's advanced analysis
            for segment_id, segment_data in analysis_results.items():
                html += f"""
                    <h3>Flight Segment {segment_id+1} Advanced Analysis</h3>
                """
                
                for axis in ['roll', 'pitch', 'yaw']:
                    if axis in segment_data:
                        plot_key = f"{segment_id}_{axis}"
                        if plot_key in advanced_plots:
                            html += f"""
                                <div class="axis-data">
                                    <h4>{axis.upper()} Axis Advanced Analysis</h4>
                                    
                                    <div class="tabs">
                            """
                            
                            # Add tabs for each analysis type
                            if 'transfer_function' in advanced_plots[plot_key]:
                                html += f"""
                                    <button class="tab-button" onclick="openTab(event, 'tf_{plot_key}')">Transfer Function</button>
                                """
                            
                            if 'arx_model' in advanced_plots[plot_key]:
                                html += f"""
                                    <button class="tab-button" onclick="openTab(event, 'arx_{plot_key}')">ARX Model</button>
                                """
                            
                            if 'wavelet' in advanced_plots[plot_key]:
                                html += f"""
                                    <button class="tab-button" onclick="openTab(event, 'wavelet_{plot_key}')">Wavelet Analysis</button>
                                """
                            
                            if 'performance' in advanced_plots[plot_key]:
                                html += f"""
                                    <button class="tab-button" onclick="openTab(event, 'perf_{plot_key}')">Performance Metrics</button>
                                """
                            
                            html += "</div>"  # End of tabs
                            
                            # Add content for each tab
                            if 'transfer_function' in advanced_plots[plot_key]:
                                html += f"""
                                    <div id="tf_{plot_key}" class="tab-content">
                                        <div class="plot">
                                            <img src="data:image/png;base64,{advanced_plots[plot_key]['transfer_function']}" alt="{axis} transfer function">
                                            <p class="plot-explanation">
                                                <b>How to interpret:</b> The top plot shows the magnitude response (how much gain at each frequency).
                                                The middle plot shows the phase response (how much delay at each frequency).
                                                The bottom plot shows the coherence (how linearly related the input and output are).
                                                Good tuning shows smooth roll-off in magnitude, good phase margin, and high coherence.
                                            </p>
                                        </div>
                                    </div>
                                """
                            
                            if 'arx_model' in advanced_plots[plot_key]:
                                html += f"""
                                    <div id="arx_{plot_key}" class="tab-content">
                                        <div class="plot">
                                            <img src="data:image/png;base64,{advanced_plots[plot_key]['arx_model']}" alt="{axis} ARX model">
                                            <p class="plot-explanation">
                                                <b>How to interpret:</b> The top plot compares actual gyro data with the model's prediction.
                                                Better fit means the model is more accurate. The bottom plot shows how the model
                                                predicts your drone would respond to a perfect step input, revealing properties like
                                                rise time and settling time.
                                            </p>
                                        </div>
                                    </div>
                                """
                            
                            if 'wavelet' in advanced_plots[plot_key]:
                                html += f"""
                                    <div id="wavelet_{plot_key}" class="tab-content">
                                        <div class="plot">
                                            <img src="data:image/png;base64,{advanced_plots[plot_key]['wavelet']}" alt="{axis} wavelet analysis">
                                            <p class="plot-explanation">
                                                <b>How to interpret:</b> The top plot (scalogram) shows power at different frequencies over time.
                                                Brighter colors indicate stronger oscillations. The bottom plot tracks the dominant frequency
                                                at each moment. Colored lines at the bottom highlight when problematic oscillations occur.
                                            </p>
                                        </div>
                                    </div>
                                """
                            
                            if 'performance' in advanced_plots[plot_key]:
                                html += f"""
                                    <div id="perf_{plot_key}" class="tab-content">
                                        <div class="plot">
                                            <img src="data:image/png;base64,{advanced_plots[plot_key]['performance']}" alt="{axis} performance metrics">
                                            <p class="plot-explanation">
                                                <b>How to interpret:</b> This chart shows performance scores in multiple categories.
                                                Higher scores (green) are better. The overall score combines all metrics into a
                                                single performance index.
                                            </p>
                                        </div>
                                    </div>
                                """
                            
                            html += """
                                </div>
                            """
                
            html += """
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