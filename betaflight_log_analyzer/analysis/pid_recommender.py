"""
Module for PID tuning recommendations
"""
import numpy as np

class PIDRecommender:
    """Class for generating PID tuning recommendations"""
    
    def __init__(self):
        """Initialize the PID recommender"""
        pass
    
    def generate_recommendations(self, analysis_results):
        """
        Generate PID tuning recommendations based on flight analysis
        
        Args:
            analysis_results: Dictionary with analysis results for each axis and segment
            
        Returns:
            Dictionary with recommendations for each axis
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
            for segment_id, segment_data in analysis_results.items():
                if axis in segment_data:
                    axis_data = segment_data[axis]
                    
                    aggregated[axis]['error_mean'].append(axis_data['error_metrics']['mean'])
                    aggregated[axis]['error_rms'].append(axis_data['error_metrics']['rms'])
                    aggregated[axis]['error_peak'].append(axis_data['error_metrics']['peak'])
                    
                    if 'frequency_analysis' in axis_data:
                        aggregated[axis]['peak_freq'].append(axis_data['frequency_analysis']['peak_freq'])
                        aggregated[axis]['peak_power'].append(axis_data['frequency_analysis']['peak_power'])
        
        # Generate recommendations for each axis
        recommendations = {}
        all_recommendations_text = {}
        
        for axis in ['roll', 'pitch', 'yaw']:
            # Skip if no data for this axis
            if not aggregated[axis]['error_rms']:
                continue
                
            # Calculate averages
            avg_error_mean = np.mean(aggregated[axis]['error_mean'])
            avg_error_rms = np.mean(aggregated[axis]['error_rms'])
            avg_error_peak = np.mean(aggregated[axis]['error_peak'])
            
            # Initialize recommendations
            p_adjustment = 0
            i_adjustment = 0
            d_adjustment = 0
            recommendations_text = []
            
            # P-term recommendations based on tracking error
            if avg_error_rms > 50:
                p_adjustment += 15
                recommendations_text.append(f"High RMS error ({avg_error_rms:.1f}): Consider increasing P by ~15%")
            elif avg_error_rms < 10:
                recommendations_text.append("Good tracking performance")
            
            # Check for oscillations
            if aggregated[axis]['peak_freq']:
                avg_peak_freq = np.mean(aggregated[axis]['peak_freq'])
                avg_peak_power = np.mean(aggregated[axis]['peak_power'])
                
                # High frequency oscillations often indicate too much D
                if avg_peak_freq > 30 and avg_peak_power > 1000:
                    d_adjustment -= 20
                    recommendations_text.append(
                        f"High frequency oscillations detected ({avg_peak_freq:.1f}Hz): Consider reducing D by ~20%"
                    )
                
                # Low frequency oscillations often indicate too much P or too little D
                elif avg_peak_freq < 10 and avg_peak_power > 1000:
                    p_adjustment -= 10
                    d_adjustment += 15
                    recommendations_text.append(
                        f"Low frequency oscillations detected ({avg_peak_freq:.1f}Hz): "
                        f"Consider reducing P by ~10% and increasing D by ~15%"
                    )
                
                # Medium frequency with high power might indicate too much P
                elif 10 <= avg_peak_freq <= 30 and avg_peak_power > 2000:
                    p_adjustment -= 10
                    recommendations_text.append(
                        f"Medium frequency oscillations detected ({avg_peak_freq:.1f}Hz): "
                        f"Consider reducing P by ~10%"
                    )
            
            # I-term recommendations based on persistent error
            if avg_error_mean > 30:
                i_adjustment += 20
                recommendations_text.append(
                    f"High average error ({avg_error_mean:.1f}): Consider increasing I by ~20%"
                )
            
            # Additional notes
            if abs(p_adjustment) < 5 and abs(i_adjustment) < 5 and abs(d_adjustment) < 5:
                recommendations_text.append("Current tune appears to be well-balanced.")
            
            if avg_error_peak > 100:
                recommendations_text.append(
                    "High peak errors detected. This could indicate mechanical issues or extreme maneuvers."
                )
            
            # Store the recommendations
            recommendations[axis] = {
                'P': p_adjustment,
                'I': i_adjustment,
                'D': d_adjustment,
                'error_metrics': {
                    'mean': avg_error_mean,
                    'rms': avg_error_rms,
                    'peak': avg_error_peak
                }
            }
            
            if aggregated[axis]['peak_freq']:
                recommendations[axis]['frequency'] = {
                    'peak_freq': avg_peak_freq,
                    'peak_power': avg_peak_power
                }
                
            all_recommendations_text[axis] = recommendations_text
        
        return recommendations, all_recommendations_text 