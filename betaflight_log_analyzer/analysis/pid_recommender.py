"""
Module for PID tuning recommendations
"""
import numpy as np

class PIDRecommender:
    """Class for generating PID tuning recommendations"""
    
    def __init__(self):
        """Initialize the PID recommender"""
        # Define confidence levels for different analysis methods
        self.confidence_weights = {
            'basic': 0.3,       # Basic error metrics
            'transfer': 0.3,    # Transfer function analysis
            'arx': 0.2,         # ARX model results
            'performance': 0.2  # Performance index metrics
        }
    
    def generate_recommendations(self, analysis_results, advanced_results=None):
        """
        Generate PID tuning recommendations based on flight analysis
        
        Args:
            analysis_results: Dictionary with analysis results for each axis and segment
            advanced_results: Optional dictionary with advanced analysis results
            
        Returns:
            Tuple of (recommendations dictionary, recommendations text dictionary)
        """
        # Check if advanced analysis is available
        has_advanced = advanced_results is not None
        
        # Aggregate results across all segments
        aggregated = self._aggregate_basic_results(analysis_results)
        
        # Aggregate advanced results if available
        advanced_aggregated = None
        if has_advanced:
            advanced_aggregated = self._aggregate_advanced_results(advanced_results)
        
        # Generate recommendations for each axis
        recommendations = {}
        all_recommendations_text = {}
        
        for axis in ['roll', 'pitch', 'yaw']:
            # Skip if no data for this axis
            if not aggregated[axis]['error_rms']:
                continue
                
            # Generate recommendations from basic metrics
            basic_rec, basic_text = self._generate_basic_recommendations(aggregated, axis)
            
            # Initialize with basic recommendations
            p_adjustment = basic_rec['P']
            i_adjustment = basic_rec['I']
            d_adjustment = basic_rec['D']
            recommendations_text = basic_text
            confidence = self.confidence_weights['basic']
            
            # Add recommendations from advanced analysis if available
            if has_advanced and axis in advanced_aggregated:
                adv_data = advanced_aggregated[axis]
                
                # Generate recommendations from transfer function
                if 'transfer_function' in adv_data:
                    tf_rec, tf_text = self._generate_tf_recommendations(adv_data['transfer_function'], axis)
                    p_adjustment = self._weighted_combine(p_adjustment, tf_rec['P'], 
                                                        self.confidence_weights['basic'], 
                                                        self.confidence_weights['transfer'])
                    d_adjustment = self._weighted_combine(d_adjustment, tf_rec['D'], 
                                                        self.confidence_weights['basic'], 
                                                        self.confidence_weights['transfer'])
                    recommendations_text.extend(tf_text)
                    confidence += self.confidence_weights['transfer']
                
                # Generate recommendations from ARX model
                if 'arx_model' in adv_data:
                    arx_rec, arx_text = self._generate_arx_model_recommendations(adv_data['arx_model'], axis)
                    p_adjustment = self._weighted_combine(p_adjustment, arx_rec['P'], 
                                                        confidence, 
                                                        self.confidence_weights['arx'])
                    i_adjustment = self._weighted_combine(i_adjustment, arx_rec['I'], 
                                                        confidence, 
                                                        self.confidence_weights['arx'])
                    d_adjustment = self._weighted_combine(d_adjustment, arx_rec['D'], 
                                                        confidence, 
                                                        self.confidence_weights['arx'])
                    recommendations_text.extend(arx_text)
                    confidence += self.confidence_weights['arx']
                
                # Generate recommendations from performance index
                if 'performance' in adv_data:
                    perf_rec, perf_text = self._generate_performance_recommendations(adv_data['performance'], axis)
                    
                    # Calculate average scores from the performance data list
                    perf_data_list = adv_data['performance']
                    tracking_scores = [data.get('tracking_score', 0) for data in perf_data_list]
                    performance_indices = [data.get('performance_index', 0) for data in perf_data_list]
                    
                    avg_tracking = np.mean(tracking_scores) if tracking_scores else 0
                    avg_performance = np.mean(performance_indices) if performance_indices else 0
                    
                    # Apply performance recommendations with high weight if scores are low
                    if avg_tracking < 60 or avg_performance < 60:
                        p_adjustment = self._weighted_combine(p_adjustment, perf_rec['P'], 
                                                            confidence, 
                                                            self.confidence_weights['performance'] * 1.5)
                        i_adjustment = self._weighted_combine(i_adjustment, perf_rec['I'], 
                                                            confidence, 
                                                            self.confidence_weights['performance'] * 1.5)
                        d_adjustment = self._weighted_combine(d_adjustment, perf_rec['D'], 
                                                            confidence, 
                                                            self.confidence_weights['performance'] * 1.5)
                        recommendations_text.extend(perf_text)
                        confidence += self.confidence_weights['performance']
            
            # Round adjustments to integer values
            p_adjustment = round(p_adjustment)
            i_adjustment = round(i_adjustment)
            d_adjustment = round(d_adjustment)
            
            # Resolve conflicts and add explanation
            conflict_explanation = self._resolve_conflicts(recommendations_text, p_adjustment, i_adjustment, d_adjustment)
            if conflict_explanation:
                recommendations_text.append(conflict_explanation)
            
            # Store the recommendations
            recommendations[axis] = {
                'P': p_adjustment,
                'I': i_adjustment,
                'D': d_adjustment,
                'error_metrics': {
                    'mean': np.mean(aggregated[axis]['error_mean']),
                    'rms': np.mean(aggregated[axis]['error_rms']),
                    'peak': np.mean(aggregated[axis]['error_peak'])
                },
                'confidence': min(confidence, 1.0)  # Cap confidence at 100%
            }
            
            if aggregated[axis]['peak_freq']:
                recommendations[axis]['frequency'] = {
                    'peak_freq': np.mean(aggregated[axis]['peak_freq']),
                    'peak_power': np.mean(aggregated[axis]['peak_power'])
                }
                
            # Add prioritization recommendation
            priority_term, priority_reason = self._prioritize_adjustment(p_adjustment, i_adjustment, d_adjustment, axis)
            
            # Determine if the tune is good or not
            is_well_tuned = (abs(p_adjustment) <= 5 and abs(i_adjustment) <= 5 and abs(d_adjustment) <= 5)
            
            # Create a simplified summary focused on what to change
            simple_summary = []
            if is_well_tuned:
                simple_summary.append(f"Your {axis.upper()} axis appears to be well-tuned! No significant adjustments needed.")
                # Add reasons why it's considered well-tuned
                if aggregated[axis]['error_rms'] and np.mean(aggregated[axis]['error_rms']) < 10:
                    simple_summary.append(f"- Low tracking error (RMS: {np.mean(aggregated[axis]['error_rms']):.1f})")
                if 'peak_power' in aggregated[axis] and aggregated[axis]['peak_power'] and np.mean(aggregated[axis]['peak_power']) < 100:
                    simple_summary.append(f"- Low oscillations (power: {np.mean(aggregated[axis]['peak_power']):.1f})")
            else:
                # Create an actionable summary
                if priority_term:
                    # Add the primary recommendation with WHAT and WHY
                    if priority_term == 'P':
                        adjustment = p_adjustment
                    elif priority_term == 'I':
                        adjustment = i_adjustment
                    else:  # D term
                        adjustment = d_adjustment
                        
                    direction = "Increase" if adjustment > 0 else "Decrease"
                    simple_summary.append(f"RECOMMENDED ACTION: {direction} {priority_term} by {abs(adjustment)}% [Adjust first]")
                    simple_summary.append(f"- {priority_reason}")
                    
                    # Add secondary adjustments if significant
                    if priority_term != 'P' and abs(p_adjustment) > 5:
                        simple_summary.append(f"- After testing, also {'increase' if p_adjustment > 0 else 'decrease'} P by {abs(p_adjustment)}%")
                    if priority_term != 'I' and abs(i_adjustment) > 5:
                        simple_summary.append(f"- After testing, also {'increase' if i_adjustment > 0 else 'decrease'} I by {abs(i_adjustment)}%")
                    if priority_term != 'D' and abs(d_adjustment) > 5:
                        simple_summary.append(f"- After testing, also {'increase' if d_adjustment > 0 else 'decrease'} D by {abs(d_adjustment)}%")
                else:
                    # Generic tune is off but no priority identified
                    simple_summary.append(f"Your {axis.upper()} axis tuning could be improved, but only minor adjustments are recommended:")
                    if p_adjustment != 0:
                        simple_summary.append(f"- {'Increase' if p_adjustment > 0 else 'Decrease'} P by {abs(p_adjustment)}%")
                    if i_adjustment != 0:
                        simple_summary.append(f"- {'Increase' if i_adjustment > 0 else 'Decrease'} I by {abs(i_adjustment)}%")
                    if d_adjustment != 0:
                        simple_summary.append(f"- {'Increase' if d_adjustment > 0 else 'Decrease'} D by {abs(d_adjustment)}%")
            
            # Add the summary to the recommendations
            recommendations[axis]['simple_summary'] = simple_summary
            
            # Add confidence level to recommendations text
            confidence_percent = min(confidence, 1.0) * 100
            confidence_text = f"Recommendation confidence: {confidence_percent:.0f}%"
            if has_advanced:
                if confidence_percent >= 80:
                    confidence_text += " (High - based on comprehensive analysis)"
                elif confidence_percent >= 60:
                    confidence_text += " (Medium - based on multiple analysis methods)"
                else:
                    confidence_text += " (Low - limited analysis available)"
            else:
                confidence_text += " (Based on basic analysis only)"
                
            all_recommendations_text[axis] = recommendations_text
            all_recommendations_text[axis].append(confidence_text)
            
            # Print out recommendations for the axis
            self._print_recommendations(axis, recommendations[axis], recommendations_text)
        
        # Print a clear bottom line summary for all axes
        print("\n" + "="*50)
        print("SUMMARY: WHAT TO CHANGE")
        print("="*50)
        for axis in ['roll', 'pitch', 'yaw']:
            if axis in recommendations:
                print(f"\n{axis.upper()} AXIS:")
                for line in recommendations[axis]['simple_summary']:
                    print(line)
        
        return recommendations, all_recommendations_text
    
    def _aggregate_basic_results(self, analysis_results):
        """Aggregate basic analysis results across all segments"""
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
        
        return aggregated
    
    def _aggregate_advanced_results(self, advanced_results):
        """Aggregate advanced analysis results across all segments"""
        aggregated = {}
        
        # Process each axis and segment
        for plot_key, data in advanced_results.items():
            # Extract axis and segment_id from plot_key (format: "{segment_id}_{axis}")
            segment_id, axis = plot_key.split('_')
            
            if axis not in aggregated:
                aggregated[axis] = {}
            
            # For each analysis type, store the results
            for analysis_type in ['transfer_function', 'arx_model', 'wavelet', 'performance']:
                if analysis_type in data:
                    if analysis_type not in aggregated[axis]:
                        aggregated[axis][analysis_type] = []
                    aggregated[axis][analysis_type].append(data[analysis_type])
        
        return aggregated
    
    def _generate_basic_recommendations(self, aggregated, axis):
        """Generate recommendations based on basic metrics"""
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
            recommendations_text.append("Current tune appears to be well-balanced based on basic metrics.")
        
        if avg_error_peak > 100:
            recommendations_text.append(
                "High peak errors detected. This could indicate mechanical issues or extreme maneuvers."
            )
        
        return {
            'P': p_adjustment,
            'I': i_adjustment,
            'D': d_adjustment
        }, recommendations_text
    
    def _generate_tf_recommendations(self, tf_data_list, axis):
        """
        Generate recommendations based on transfer function analysis
        
        Args:
            tf_data_list: List of transfer function results from different segments
            axis: Axis name (roll, pitch, yaw)
            
        Returns:
            Tuple of (recommendations dictionary, recommendations text list)
        """
        # Initialize recommendations
        p_adjustment = 0
        d_adjustment = 0
        recommendations_text = []
        
        # Calculate average phase margin and resonant frequencies
        phase_margins = []
        resonant_freqs = []
        coherence_values = []
        
        for tf_data in tf_data_list:
            if 'phase_margin' in tf_data:
                phase_margins.append(tf_data['phase_margin'])
            
            if 'resonant_frequencies' in tf_data and tf_data['resonant_frequencies']:
                # Extract frequencies and magnitudes
                for freq, mag in tf_data['resonant_frequencies']:
                    resonant_freqs.append((freq, mag))
            
            # Calculate average coherence at low frequencies (0-20Hz)
            freqs = tf_data['frequencies']
            coherence = tf_data['coherence']
            low_freq_mask = (freqs > 0) & (freqs < 20)
            if np.any(low_freq_mask):
                avg_coherence = np.mean(coherence[low_freq_mask])
                coherence_values.append(avg_coherence)
        
        # Analyze phase margin
        if phase_margins:
            avg_phase_margin = np.mean(phase_margins)
            
            # Ideal phase margin is 45-60 degrees
            if avg_phase_margin < 30:
                p_adjustment -= 15
                d_adjustment += 20
                recommendations_text.append(
                    f"Low phase margin ({avg_phase_margin:.1f}°): Reduce P by ~15% and increase D by ~20% "
                    f"to improve stability"
                )
            elif avg_phase_margin > 70:
                p_adjustment += 10
                recommendations_text.append(
                    f"High phase margin ({avg_phase_margin:.1f}°): System is overdamped, "
                    f"consider increasing P by ~10% for better responsiveness"
                )
            else:
                recommendations_text.append(
                    f"Good phase margin ({avg_phase_margin:.1f}°): System has good stability reserves"
                )
        
        # Analyze resonant frequencies
        if resonant_freqs:
            # Group by frequency range
            low_res = [m for f, m in resonant_freqs if f < 10]
            mid_res = [m for f, m in resonant_freqs if 10 <= f < 30]
            high_res = [m for f, m in resonant_freqs if f >= 30]
            
            # Check for strong resonances
            if low_res and np.max(low_res) > 3.0:
                p_adjustment -= 15
                recommendations_text.append(
                    f"Strong low-frequency resonance detected: Consider reducing P by ~15%"
                )
            
            if mid_res and np.max(mid_res) > 2.5:
                p_adjustment -= 10
                d_adjustment += 10
                recommendations_text.append(
                    f"Mid-frequency resonance detected: Consider reducing P by ~10% and increasing D by ~10%"
                )
            
            if high_res and np.max(high_res) > 2.0:
                d_adjustment -= 20
                recommendations_text.append(
                    f"High-frequency resonance detected: Consider reducing D by ~20%"
                )
        
        # Analyze coherence
        if coherence_values:
            avg_coherence = np.mean(coherence_values)
            if avg_coherence < 0.5:
                recommendations_text.append(
                    f"Low input-output coherence ({avg_coherence:.2f}): System behavior is nonlinear or "
                    f"there's significant noise in the signal. Mechanical issues may be present."
                )
        
        if not recommendations_text:
            recommendations_text.append(
                f"Transfer function analysis shows no significant issues for {axis.upper()} axis."
            )
        
        return {
            'P': p_adjustment,
            'D': d_adjustment
        }, recommendations_text
    
    def _generate_arx_model_recommendations(self, arx_data_list, axis):
        """
        Generate recommendations based on ARX model results
        
        Args:
            arx_data_list: List of ARX model results from different segments
            axis: Axis name (roll, pitch, yaw)
            
        Returns:
            Tuple of (recommendations dictionary, recommendations text list)
        """
        # Initialize recommendations
        p_adjustment = 0
        i_adjustment = 0
        d_adjustment = 0
        recommendations_text = []
        
        # Calculate average fit quality
        fit_values = [data['fit'] for data in arx_data_list]
        avg_fit = np.mean(fit_values) if fit_values else 0
        
        # If fit quality is low, recommendations may be less reliable
        if avg_fit < 40:
            recommendations_text.append(
                f"ARX model fit quality is low ({avg_fit:.1f}%): Recommendations may be less reliable"
            )
            return {
                'P': 0,
                'I': 0,
                'D': 0
            }, recommendations_text
        
        # Analyze step responses
        rise_times = []
        settling_times = []
        overshoots = []
        
        for data in arx_data_list:
            step_response = data['step_response']
            steady_state = np.mean(step_response[-20:])
            
            # Skip if steady state is too close to zero
            if abs(steady_state) < 1e-6:
                continue
            
            # Calculate rise time (10% to 90%)
            try:
                rise_10_idx = np.where(step_response >= 0.1 * steady_state)[0][0]
                rise_90_idx = np.where(step_response >= 0.9 * steady_state)[0][0]
                rise_time = rise_90_idx - rise_10_idx
                rise_times.append(rise_time)
            except:
                pass
            
            # Calculate settling time
            try:
                settling_band = 0.05 * steady_state
                for i in range(len(step_response) - 30):
                    if all(abs(step_response[i+j] - steady_state) <= settling_band for j in range(30)):
                        settling_times.append(i)
                        break
            except:
                pass
            
            # Calculate overshoot
            try:
                if rise_90_idx and rise_90_idx < len(step_response) - 1:
                    max_response = np.max(step_response[rise_90_idx:])
                    overshoot = (max_response - steady_state) / abs(steady_state) * 100
                    overshoots.append(overshoot)
            except:
                pass
        
        # Generate recommendations based on rise time
        if rise_times:
            avg_rise_time = np.mean(rise_times)
            if avg_rise_time > 20:  # Very slow response
                p_adjustment += 25
                recommendations_text.append(
                    f"Slow system response (rise time: {avg_rise_time:.1f} samples): "
                    f"Consider increasing P by ~25%"
                )
            elif avg_rise_time > 10:  # Moderately slow response
                p_adjustment += 15
                recommendations_text.append(
                    f"Moderate system response (rise time: {avg_rise_time:.1f} samples): "
                    f"Consider increasing P by ~15%"
                )
            elif avg_rise_time < 3:  # Very fast response
                p_adjustment -= 10
                recommendations_text.append(
                    f"Very fast system response (rise time: {avg_rise_time:.1f} samples): "
                    f"Consider decreasing P by ~10%"
                )
        
        # Generate recommendations based on overshoot
        if overshoots:
            avg_overshoot = np.mean(overshoots)
            if avg_overshoot > 30:  # High overshoot
                p_adjustment -= 20
                d_adjustment += 15
                recommendations_text.append(
                    f"High system overshoot ({avg_overshoot:.1f}%): "
                    f"Consider decreasing P by ~20% and increasing D by ~15%"
                )
            elif avg_overshoot > 15:  # Moderate overshoot
                p_adjustment -= 10
                d_adjustment += 10
                recommendations_text.append(
                    f"Moderate system overshoot ({avg_overshoot:.1f}%): "
                    f"Consider decreasing P by ~10% and increasing D by ~10%"
                )
            elif avg_overshoot < 5:  # Low overshoot
                p_adjustment += 5
                recommendations_text.append(
                    f"Low system overshoot ({avg_overshoot:.1f}%): "
                    f"Consider increasing P by ~5% for better responsiveness"
                )
        
        # Generate recommendations based on settling time
        if settling_times:
            avg_settling_time = np.mean(settling_times)
            if avg_settling_time > 50:  # Very slow settling
                i_adjustment += 20
                recommendations_text.append(
                    f"Slow system settling (settling time: {avg_settling_time:.1f} samples): "
                    f"Consider increasing I by ~20%"
                )
            elif avg_settling_time > 30:  # Moderately slow settling
                i_adjustment += 10
                recommendations_text.append(
                    f"Moderate system settling (settling time: {avg_settling_time:.1f} samples): "
                    f"Consider increasing I by ~10%"
                )
        
        if not recommendations_text:
            recommendations_text.append(
                f"ARX model analysis suggests good step response characteristics for {axis.upper()} axis."
            )
        
        return {
            'P': p_adjustment,
            'I': i_adjustment,
            'D': d_adjustment
        }, recommendations_text
    
    def _generate_performance_recommendations(self, perf_data_list, axis):
        """
        Generate recommendations based on performance index metrics
        
        Args:
            perf_data_list: List of performance index results from different segments
            axis: Axis name (roll, pitch, yaw)
            
        Returns:
            Tuple of (recommendations dictionary, recommendations text list)
        """
        # Initialize recommendations
        p_adjustment = 0
        i_adjustment = 0
        d_adjustment = 0
        recommendations_text = []
        
        # Check if there's valid performance data
        if not perf_data_list or len(perf_data_list) == 0:
            recommendations_text.append(
                f"No performance data available for {axis.upper()} axis."
            )
            return {
                'P': 0,
                'I': 0,
                'D': 0
            }, recommendations_text
        
        # Calculate average performance metrics
        tracking_scores = [data.get('tracking_score', 0) for data in perf_data_list]
        noise_scores = [data.get('noise_score', 0) for data in perf_data_list]
        response_scores = [data.get('response_score', 0) for data in perf_data_list]
        performance_indices = [data.get('performance_index', 0) for data in perf_data_list]
        
        avg_tracking = np.mean(tracking_scores) if tracking_scores else 0
        avg_noise = np.mean(noise_scores) if noise_scores else 0
        avg_response = np.mean(response_scores) if response_scores else 0
        avg_performance = np.mean(performance_indices) if performance_indices else 0
        
        # Generate recommendations based on tracking score
        if avg_tracking < 40:  # Very poor tracking
            p_adjustment += 25
            i_adjustment += 15
            recommendations_text.append(
                f"Very poor tracking performance (score: {avg_tracking:.1f}): "
                f"Consider increasing P by ~25% and I by ~15%"
            )
        elif avg_tracking < 60:  # Poor tracking
            p_adjustment += 15
            i_adjustment += 10
            recommendations_text.append(
                f"Poor tracking performance (score: {avg_tracking:.1f}): "
                f"Consider increasing P by ~15% and I by ~10%"
            )
        elif avg_tracking > 80:  # Excellent tracking
            recommendations_text.append(
                f"Excellent tracking performance (score: {avg_tracking:.1f})"
            )
        
        # Generate recommendations based on noise score
        if avg_noise < 40:  # High noise
            d_adjustment -= 25
            recommendations_text.append(
                f"High noise/vibration detected (score: {avg_noise:.1f}): "
                f"Consider reducing D by ~25%"
            )
        elif avg_noise < 60:  # Moderate noise
            d_adjustment -= 15
            recommendations_text.append(
                f"Moderate noise/vibration detected (score: {avg_noise:.1f}): "
                f"Consider reducing D by ~15%"
            )
        elif avg_noise > 80:  # Low noise
            recommendations_text.append(
                f"Excellent noise performance (score: {avg_noise:.1f})"
            )
        
        # Generate recommendations based on responsiveness score
        if avg_response < 40:  # Poor responsiveness
            p_adjustment += 20
            d_adjustment -= 10
            recommendations_text.append(
                f"Poor responsiveness (score: {avg_response:.1f}): "
                f"Consider increasing P by ~20% and reducing D by ~10%"
            )
        elif avg_response < 60:  # Moderate responsiveness
            p_adjustment += 10
            recommendations_text.append(
                f"Moderate responsiveness (score: {avg_response:.1f}): "
                f"Consider increasing P by ~10%"
            )
        
        # Overall performance assessment
        if avg_performance > 80:
            recommendations_text.append(
                f"Overall performance is excellent ({avg_performance:.1f}). "
                f"Only minor PID adjustments may be needed."
            )
        elif avg_performance < 50:
            recommendations_text.append(
                f"Overall performance is poor ({avg_performance:.1f}). "
                f"Significant PID adjustments are recommended."
            )
        
        if not recommendations_text:
            recommendations_text.append(
                f"Performance metrics suggest good overall performance for {axis.upper()} axis."
            )
        
        return {
            'P': p_adjustment,
            'I': i_adjustment,
            'D': d_adjustment
        }, recommendations_text
    
    def _weighted_combine(self, value1, value2, weight1, weight2):
        """
        Combine two values using weighted average with safeguards
        
        Args:
            value1: First value 
            value2: Second value
            weight1: Weight for first value
            weight2: Weight for second value
            
        Returns:
            Weighted average of the two values
        """
        # Ensure weights are positive
        weight1 = max(0, weight1)
        weight2 = max(0, weight2)
        
        # Calculate total weight
        total_weight = weight1 + weight2
        
        # If total weight is zero or very small, use simple average
        if total_weight < 0.01:
            return (value1 + value2) / 2
            
        # Compute weighted average
        result = (value1 * weight1 + value2 * weight2) / total_weight
        
        # When values have opposite signs (conflicting recommendations),
        # prioritize larger magnitude with higher weight
        if value1 * value2 < 0:
            # If one value's magnitude is significantly larger and has higher weight,
            # bias towards that value more
            mag1 = abs(value1)
            mag2 = abs(value2)
            
            if mag1 > 2 * mag2 and weight1 >= weight2:
                # Value1 is dominant in magnitude and weight
                result = 0.8 * value1 + 0.2 * result
            elif mag2 > 2 * mag1 and weight2 >= weight1:
                # Value2 is dominant in magnitude and weight
                result = 0.8 * value2 + 0.2 * result
        
        return result
    
    def _print_recommendations(self, axis, recommendations, text):
        """Print detailed recommendations for an axis"""
        print(f"\n{axis.upper()} Axis - DETAILED Analysis:")
        
        # Print basic metrics
        print(f"Average error metrics: mean={recommendations['error_metrics']['mean']:.1f}, "
              f"RMS={recommendations['error_metrics']['rms']:.1f}, "
              f"peak={recommendations['error_metrics']['peak']:.1f}")
        
        # Print frequency information if available
        if 'frequency' in recommendations:
            print(f"Average dominant frequency: {recommendations['frequency']['peak_freq']:.1f}Hz, "
                 f"power: {recommendations['frequency']['peak_power']:.1f}")
        
        # Print specific recommendations
        for rec in text:
            if isinstance(rec, str):  # Make sure it's a string
                print(f"- {rec}")
        
        # Print PID adjustments
        print("\nCalculated PID adjustments:")
        print(f"P: {recommendations['P']:+d}%")
        print(f"I: {recommendations['I']:+d}%")
        print(f"D: {recommendations['D']:+d}%")
    
    def _resolve_conflicts(self, recommendations_text, p_adjustment, i_adjustment, d_adjustment):
        """
        Resolve conflicts between recommendations and add explanation
        
        Args:
            recommendations_text: List of text recommendations
            p_adjustment: Final P adjustment percentage
            i_adjustment: Final I adjustment percentage
            d_adjustment: Final D adjustment percentage
            
        Returns:
            String with conflict explanation or None if no conflict detected
        """
        # Check for conflicts by looking for contradictory phrases in recommendations
        increase_p = any("increasing P" in rec.lower() for rec in recommendations_text)
        decrease_p = any("reducing P" in rec.lower() or "decreasing P" in rec.lower() for rec in recommendations_text)
        
        increase_i = any("increasing I" in rec.lower() for rec in recommendations_text)
        decrease_i = any("reducing I" in rec.lower() or "decreasing I" in rec.lower() for rec in recommendations_text)
        
        increase_d = any("increasing D" in rec.lower() for rec in recommendations_text)
        decrease_d = any("reducing D" in rec.lower() or "decreasing D" in rec.lower() for rec in recommendations_text)
        
        # Build explanation for P-term conflicts
        explanation = []
        
        if increase_p and decrease_p:
            if p_adjustment > 0:
                explanation.append("Conflicting P recommendations detected: Prioritizing responsiveness over stability.")
            elif p_adjustment < 0:
                explanation.append("Conflicting P recommendations detected: Prioritizing stability over responsiveness.")
            else:  # p_adjustment == 0
                explanation.append("Conflicting P recommendations balanced out to no change.")
        
        # Build explanation for I-term conflicts
        if increase_i and decrease_i:
            if i_adjustment > 0:
                explanation.append("Conflicting I recommendations detected: Prioritizing steady-state accuracy.")
            elif i_adjustment < 0:
                explanation.append("Conflicting I recommendations detected: Prioritizing reducing steady-state oscillation.")
            else:  # i_adjustment == 0
                explanation.append("Conflicting I recommendations balanced out to no change.")
        
        # Build explanation for D-term conflicts
        if increase_d and decrease_d:
            if d_adjustment > 0:
                explanation.append("Conflicting D recommendations detected: Prioritizing damping and stability.")
            elif d_adjustment < 0:
                explanation.append("Conflicting D recommendations detected: Prioritizing noise reduction.")
            else:  # d_adjustment == 0
                explanation.append("Conflicting D recommendations balanced out to no change.")
                
        # Check if final adjustments match the recommendations direction
        if increase_p and not decrease_p and p_adjustment <= 0:
            explanation.append("P increase was recommended but weighted down by other factors.")
        if not increase_p and decrease_p and p_adjustment >= 0:
            explanation.append("P decrease was recommended but weighted out by other factors.")
            
        if increase_i and not decrease_i and i_adjustment <= 0:
            explanation.append("I increase was recommended but weighted down by other factors.")
        if not increase_i and decrease_i and i_adjustment >= 0:
            explanation.append("I decrease was recommended but weighted out by other factors.")
            
        if increase_d and not decrease_d and d_adjustment <= 0:
            explanation.append("D increase was recommended but weighted down by other factors.")
        if not increase_d and decrease_d and d_adjustment >= 0:
            explanation.append("D decrease was recommended but weighted out by other factors.")
        
        # Summarize trade-offs for zero adjustments with conflicting recommendations
        has_conflict = increase_p and decrease_p or increase_i and decrease_i or increase_d and decrease_d
        has_zero_with_rec = (p_adjustment == 0 and (increase_p or decrease_p)) or \
                           (i_adjustment == 0 and (increase_i or decrease_i)) or \
                           (d_adjustment == 0 and (increase_d or decrease_d))
                            
        if has_conflict or has_zero_with_rec:
            explanation.append("Remember that PID tuning involves trade-offs between responsiveness, stability, and noise rejection.")
        
        return "\n".join(explanation) if explanation else None
    
    def _prioritize_adjustment(self, p_adjustment, i_adjustment, d_adjustment, axis):
        """
        Prioritize which PID term should be adjusted first
        
        Args:
            p_adjustment: Final P adjustment percentage
            i_adjustment: Final I adjustment percentage
            d_adjustment: Final D adjustment percentage
            axis: Axis name (roll, pitch, yaw)
            
        Returns:
            Tuple of (prioritized term, reason) or None if no adjustment recommended
        """
        # If no adjustments are recommended, return None
        if p_adjustment == 0 and i_adjustment == 0 and d_adjustment == 0:
            return None, None
            
        # Store the absolute magnitude of each adjustment
        adjustments = {
            'P': abs(p_adjustment),
            'I': abs(i_adjustment),
            'D': abs(d_adjustment)
        }
        
        # Find the term with the largest adjustment 
        max_term = max(adjustments, key=adjustments.get)
        max_value = adjustments[max_term]
        
        # If the largest adjustment is zero, return None
        if max_value == 0:
            return None, None
            
        # Generate specific reason based on the term and direction
        if max_term == 'P':
            if p_adjustment > 0:
                reason = f"Increase P by {p_adjustment}% to improve responsiveness."
            else:
                reason = f"Decrease P by {abs(p_adjustment)}% to reduce oscillations."
        elif max_term == 'I':
            if i_adjustment > 0:
                reason = f"Increase I by {i_adjustment}% to improve steady-state tracking."
            else:
                reason = f"Decrease I by {abs(i_adjustment)}% to reduce I-term buildup."
        else:  # max_term == 'D'
            if d_adjustment > 0:
                reason = f"Increase D by {d_adjustment}% to improve damping."
            else:
                reason = f"Decrease D by {abs(d_adjustment)}% to reduce noise amplification."
                
        # Special case: if D is negative with a significant value, prioritize it
        # as noise issues should often be addressed first
        if d_adjustment < -10 and 'D' in adjustments and adjustments['D'] >= max_value * 0.7:
            max_term = 'D'
            reason = f"Decrease D by {abs(d_adjustment)}% to reduce noise amplification. Noise should be addressed before other tuning."
        
        # Special case: for very small adjustments, suggest focusing on other aspects
        if max_value < 5:
            additional = "This is a relatively small adjustment, which indicates the current tune is reasonable."
            reason = f"{reason} {additional}"
            
        return max_term, reason 