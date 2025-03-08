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
        
        # Create HTML report focusing on step response functions
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Betaflight PID Analysis - {self.log_name}</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    margin: 0;
                    padding: 20px;
                    color: #333;
                    line-height: 1.6;
                    max-width: 1200px;
                    margin: 0 auto;
                }}
                
                h1, h2, h3 {{
                    color: #2c3e50;
                    margin-top: 15px;
                    font-weight: 600;
                }}
                
                header {{
                    background-color: #2c3e50;
                    color: white;
                    padding: 20px;
                    margin-bottom: 20px;
                    border-radius: 5px;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                }}
                
                header h1 {{
                    color: white;
                    margin: 0;
                }}
                
                .summary-box {{
                    background-color: #f8f9fa;
                    padding: 15px;
                    border-radius: 5px;
                    margin-bottom: 20px;
                    border-left: 5px solid #2c3e50;
                }}
                
                .good-tune {{
                    background-color: #e9ffe9;
                    padding: 15px;
                    border-radius: 5px;
                    margin-bottom: 10px;
                    border-left: 5px solid #27ae60;
                }}
                
                .needs-tune {{
                    background-color: #fff0e9;
                    padding: 15px;
                    border-radius: 5px;
                    margin-bottom: 10px;
                    border-left: 5px solid #e67e22;
                }}
                
                .axis-box {{
                    margin-bottom: 30px;
                    padding: 15px;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.05);
                }}
                
                .axis-title {{
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }}
                
                .pid-values {{
                    background-color: #f8f9fa;
                    padding: 10px;
                    border-radius: 3px;
                    font-family: monospace;
                    margin: 10px 0;
                }}
                
                .step-response {{
                    margin: 20px 0;
                }}
                
                .step-response img {{
                    max-width: 100%;
                    height: auto;
                    border: 1px solid #eee;
                    border-radius: 3px;
                }}
                
                .interpretation {{
                    background-color: #f0f7ff;
                    padding: 15px;
                    border-radius: 5px;
                    margin: 10px 0;
                    border-left: 3px solid #3498db;
                }}
                
                .recommendation {{
                    font-weight: bold;
                }}
                
                .footer {{
                    margin-top: 30px;
                    padding-top: 10px;
                    border-top: 1px solid #eee;
                    text-align: center;
                    font-size: 0.9em;
                    color: #777;
                }}
                
                .metrics {{
                    display: flex;
                    flex-wrap: wrap;
                    gap: 15px;
                    margin: 15px 0;
                }}
                
                .metric-card {{
                    flex: 1;
                    min-width: 150px;
                    padding: 10px;
                    background-color: #f8f9fa;
                    border-radius: 5px;
                    border: 1px solid #eee;
                }}
                
                .metric-name {{
                    font-weight: bold;
                    margin-bottom: 5px;
                }}
                
                .metric-value {{
                    font-size: 1.2em;
                    font-family: monospace;
                }}
                
                .detailed-explanation {{
                    background-color: #fff8ec;
                    padding: 15px;
                    border-radius: 5px;
                    margin: 15px 0;
                    border-left: 3px solid #e67e22;
                    font-size: 0.95em;
                }}
                
                .detailed-explanation h4 {{
                    color: #e67e22;
                    margin-top: 0;
                    margin-bottom: 10px;
                }}
                
                .detailed-explanation ul {{
                    margin-top: 5px;
                    padding-left: 20px;
                }}
                
                .detailed-explanation li {{
                    margin-bottom: 8px;
                    line-height: 1.4;
                }}
                
                @media (max-width: 768px) {{
                    .metrics {{
                        flex-direction: column;
                    }}
                }}
            </style>
        </head>
        <body>
            <header>
                <h1>PID Analysis Report - {os.path.basename(self.log_file_path)}</h1>
                <p>Generated on {timestamp}</p>
            </header>
            
            <div class="summary-box">
                <h2>Tuning Recommendations Summary</h2>
        """
        
        # Add key recommendations first
        for axis in ['roll', 'pitch', 'yaw']:
            if axis in recommendations:
                rec = recommendations[axis]
                
                # Check if we have simple_summary available to determine if axis is well-tuned
                is_well_tuned = False
                if 'simple_summary' in rec and rec['simple_summary']:
                    is_well_tuned = rec['simple_summary'][0].startswith(f"Your {axis.upper()} axis appears to be well-tuned")
                # Otherwise, fallback to the older logic (minor adjustments indicate well-tuned)
                else:
                    is_well_tuned = abs(rec['P']) <= 5 and abs(rec['I']) <= 5 and abs(rec['D']) <= 5
                
                css_class = "good-tune" if is_well_tuned else "needs-tune"
                html += f"""
                <div class="{css_class}">
                    <h3>{axis.upper()} Axis: {'Well Tuned' if is_well_tuned else 'Needs Adjustment'}</h3>
                    <div class="pid-values">
                        Recommended changes: P: {rec['P']:+d}%, I: {rec['I']:+d}%, D: {rec['D']:+d}%
                    </div>
                """
                
                # Add actionable recommendations if available
                if 'simple_summary' in rec and rec['simple_summary']:
                    html += "<ul>"
                    for line in rec['simple_summary']:
                        # Skip the first line if it's just saying it's well-tuned (redundant with our header)
                        if line.startswith(f"Your {axis.upper()} axis appears to be well-tuned"):
                            continue
                        html += f"<li>{line}</li>"
                    html += "</ul>"
                
                # Add detailed explanation of why changes are recommended
                if not is_well_tuned:
                    # Prepare detailed explanations
                    detailed_reasons = []
                    
                    # Add different types of reasons based on the axis
                    if axis == 'yaw' and rec['P'] > 0:
                        # Extract key metrics from the detailed text
                        rise_time = None
                        overshoot = None
                        phase_margin = None
                        settling_time = None
                        
                        # Parse recommendation text to extract values
                        for text in recommendations_text.get(axis, []):
                            if "rise time" in text:
                                try:
                                    rise_time = text.split("(rise time: ")[1].split(" samples")[0]
                                except:
                                    pass
                            if "overshoot" in text:
                                try:
                                    overshoot = text.split("(")[1].split(")")[0]
                                except:
                                    pass
                            if "phase margin" in text:
                                try:
                                    phase_margin = text.split("(")[1].split("°")[0]
                                except:
                                    pass
                            if "settling time" in text:
                                try:
                                    settling_time = text.split("(settling time: ")[1].split(" samples")[0]
                                except:
                                    pass
                        
                        # Add detailed explanations
                        html += """
                        <div class="detailed-explanation">
                            <h4>Why This Change Is Recommended:</h4>
                            <ul>
                        """
                        
                        if rise_time:
                            html += f"<li><strong>Slow rise time:</strong> {rise_time} samples indicates the yaw axis is responding too slowly to inputs.</li>"
                        
                        if phase_margin and float(phase_margin) > 70:
                            html += f"<li><strong>High phase margin:</strong> {phase_margin}° suggests the system is overdamped and could be more responsive.</li>"
                        
                        if overshoot and "0.0%" in overshoot:
                            html += f"<li><strong>Low overshoot:</strong> {overshoot} indicates the system is too conservative and could respond faster.</li>"
                        
                        if settling_time:
                            html += f"<li><strong>Moderate settling time:</strong> {settling_time} samples shows the system takes time to stabilize.</li>"
                        
                        html += """
                            </ul>
                        </div>
                        """
                    
                    # For ROLL and PITCH axes, add general explanations
                    elif (axis == 'roll' or axis == 'pitch') and (abs(rec['P']) > 0 or abs(rec['D']) > 0):
                        html += """
                        <div class="detailed-explanation">
                            <h4>Why This Change Is Recommended:</h4>
                            <ul>
                        """
                        
                        if rec['P'] > 0:
                            html += "<li><strong>P value increase:</strong> The phase margin suggests an overdamped system that could be more responsive.</li>"
                        elif rec['P'] < 0:
                            html += "<li><strong>P value decrease:</strong> Resonances detected in the frequency analysis suggest the P gain may be too high.</li>"
                        
                        if rec['D'] > 0:
                            html += "<li><strong>D value increase:</strong> Mid-frequency resonances suggest more damping would help control oscillations.</li>"
                        elif rec['D'] < 0:
                            html += "<li><strong>D value decrease:</strong> High-frequency noise detected suggests reducing D to minimize noise amplification.</li>"
                        
                        html += """
                            </ul>
                        </div>
                        """
                
                html += """
                </div>
                """
        
        html += """
                <div class="interpretation">
                    <p><strong>How to read step response:</strong> The step response shows how your drone's gyro responds to a sudden change in setpoint. 
                    Look for:</p>
                    <ul>
                        <li><strong>Rise time:</strong> How quickly the response reaches the setpoint</li>
                        <li><strong>Overshoot:</strong> How much the response exceeds the setpoint</li>
                        <li><strong>Settling time:</strong> How long it takes to stabilize at the setpoint</li>
                    </ul>
                    <p>Ideal response: Quick rise time with minimal overshoot and fast settling.</p>
                </div>
            </div>
        """
        
        # Add detailed axis analysis with step responses
        html += """
            <h2>Step Response Analysis</h2>
        """
        
        # Find the best segment for each axis (usually the one with the best ARX model fit)
        best_segments = {}
        if has_advanced:
            for plot_key, data in advanced_results.items():
                if 'arx_model' in data:
                    try:
                        segment_id, axis = plot_key.split('_')
                        segment_id = int(segment_id)
                        
                        # Store the first segment found for each axis
                        if axis not in best_segments:
                            best_segments[axis] = (segment_id, data['arx_model'].get('fit', 0))
                        # Update if better fit is found
                        elif 'fit' in data['arx_model'] and data['arx_model']['fit'] > best_segments[axis][1]:
                            best_segments[axis] = (segment_id, data['arx_model']['fit'])
                    except (ValueError, AttributeError):
                        # Skip this entry if it's not properly formatted
                        continue
        
        # Add step response for each axis
        for axis in ['roll', 'pitch', 'yaw']:
            if axis in recommendations:
                rec = recommendations[axis]
                
                html += f"""
                <div class="axis-box">
                    <div class="axis-title">
                        <h3>{axis.upper()} Axis Analysis</h3>
                    </div>
                    
                    <div class="metrics">
                        <div class="metric-card">
                            <div class="metric-name">RMS Error</div>
                            <div class="metric-value">{rec['error_metrics']['rms']:.1f}</div>
                        </div>
                """
                
                if 'frequency' in rec:
                    html += f"""
                        <div class="metric-card">
                            <div class="metric-name">Peak Freq</div>
                            <div class="metric-value">{rec['frequency']['peak_freq']:.1f} Hz</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-name">Peak Power</div>
                            <div class="metric-value">{rec['frequency']['peak_power']:.1f}</div>
                        </div>
                    """
                
                html += """
                    </div>
                """
                
                # Add the step response plot if available
                if has_advanced and axis in best_segments:
                    segment_id = best_segments[axis][0]
                    plot_key = f"{segment_id}_{axis}"
                    
                    if plot_key in advanced_plots and 'arx_model' in advanced_plots[plot_key]:
                        html += f"""
                        <div class="step-response">
                            <h4>Step Response (Segment {segment_id+1})</h4>
                            <img src="data:image/png;base64,{advanced_plots[plot_key]['arx_model']}" alt="{axis} step response">
                        </div>
                        """
                
                html += """
                </div>
                """
        
        # Add tips for improving tune based on step response
        html += """
            <div class="interpretation">
                <h3>How to Interpret Step Response Plots</h3>
                <p>The upper plot shows actual vs. predicted gyro data. Better fit means the model is more accurate.</p>
                <p>The lower plot shows the step response:</p>
                <ul>
                    <li><strong>Slow rise time?</strong> Increase P for faster response</li>
                    <li><strong>Too much overshoot?</strong> Reduce P or increase D</li>
                    <li><strong>Oscillations?</strong> Reduce P and possibly increase D</li>
                    <li><strong>Doesn't reach setpoint?</strong> Increase I to eliminate steady-state error</li>
                    <li><strong>Noisy response?</strong> Reduce D to decrease noise amplification</li>
                </ul>
                <p>Remember: Make only ONE change at a time, test fly, and re-log for best results.</p>
            </div>
            
            <div class="footer">
                <p>Generated by Betaflight Log Analyzer - {timestamp}</p>
            </div>
        </body>
        </html>
        """
        
        return html 