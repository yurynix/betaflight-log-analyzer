"""
Unit tests for the HTML Reporter module
"""
import os
import tempfile
import unittest
from unittest.mock import patch, MagicMock
import base64
import numpy as np

from betaflight_log_analyzer.reports.html_reporter import HTMLReporter

class TestHTMLReporter(unittest.TestCase):
    """Test class for HTMLReporter"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create a temporary directory for test outputs
        self.test_dir = tempfile.mkdtemp()
        self.log_file_path = "/path/to/LOG00042.BFL"
        
        # Create mock data for testing
        self.mock_analysis_results = self._create_mock_analysis_results()
        self.mock_recommendations = self._create_mock_recommendations()
        self.mock_recommendations_text = self._create_mock_recommendation_text()
        self.mock_segment_plots = self._create_mock_segment_plots()
        self.mock_advanced_results = self._create_mock_advanced_results()
        self.mock_advanced_plots = self._create_mock_advanced_plots()
        
        # Initialize the HTML reporter
        self.reporter = HTMLReporter(self.test_dir, self.log_file_path)
    
    def tearDown(self):
        """Clean up test fixtures"""
        # Remove test files
        for file in os.listdir(self.test_dir):
            os.remove(os.path.join(self.test_dir, file))
        os.rmdir(self.test_dir)
    
    def _create_mock_analysis_results(self):
        """Create mock analysis results for testing"""
        return {
            '0': {
                'roll': {
                    'duration': 10.5,
                    'rc_stats': {'mean': 0.0, 'std': 5.0, 'min': -10.0, 'max': 10.0},
                    'setpoint_stats': {'mean': 0.0, 'std': 10.0, 'min': -20.0, 'max': 20.0},
                    'gyro_stats': {'mean': 0.0, 'std': 8.0, 'min': -15.0, 'max': 15.0},
                    'error_metrics': {'mean': 1.5, 'rms': 3.0, 'peak': 20.0},
                    'frequency_analysis': {'peak_freq': 5.0, 'peak_power': 100.0}
                },
                'pitch': {
                    'duration': 10.5,
                    'rc_stats': {'mean': 0.0, 'std': 5.0, 'min': -10.0, 'max': 10.0},
                    'setpoint_stats': {'mean': 0.0, 'std': 10.0, 'min': -20.0, 'max': 20.0},
                    'gyro_stats': {'mean': 0.0, 'std': 8.0, 'min': -15.0, 'max': 15.0},
                    'error_metrics': {'mean': 1.0, 'rms': 2.5, 'peak': 18.0},
                    'frequency_analysis': {'peak_freq': 4.0, 'peak_power': 80.0}
                },
                'yaw': {
                    'duration': 10.5,
                    'rc_stats': {'mean': 0.0, 'std': 5.0, 'min': -10.0, 'max': 10.0},
                    'setpoint_stats': {'mean': 0.0, 'std': 10.0, 'min': -20.0, 'max': 20.0},
                    'gyro_stats': {'mean': 0.0, 'std': 8.0, 'min': -15.0, 'max': 15.0},
                    'error_metrics': {'mean': 0.8, 'rms': 1.5, 'peak': 15.0},
                    'frequency_analysis': {'peak_freq': 3.0, 'peak_power': 50.0}
                }
            }
        }
    
    def _create_mock_recommendations(self):
        """Create mock recommendations for testing"""
        return {
            'roll': {
                'P': 0,
                'I': 0,
                'D': -5,
                'error_metrics': {'mean': 1.5, 'rms': 3.0, 'peak': 20.0},
                'frequency': {'peak_freq': 5.0, 'peak_power': 100.0},
                'confidence': 0.8,
                'simple_summary': [
                    "Your ROLL axis appears to be well-tuned! No significant adjustments needed.",
                    "- Low tracking error (RMS: 3.0)",
                    "- Low oscillations (power: 100.0)"
                ]
            },
            'pitch': {
                'P': 0,
                'I': 0,
                'D': -5,
                'error_metrics': {'mean': 1.0, 'rms': 2.5, 'peak': 18.0},
                'frequency': {'peak_freq': 4.0, 'peak_power': 80.0},
                'confidence': 0.8,
                'simple_summary': [
                    "Your PITCH axis appears to be well-tuned! No significant adjustments needed.",
                    "- Low tracking error (RMS: 2.5)",
                    "- Low oscillations (power: 80.0)"
                ]
            },
            'yaw': {
                'P': 10,
                'I': 5,
                'D': -5,
                'error_metrics': {'mean': 0.8, 'rms': 1.5, 'peak': 15.0},
                'frequency': {'peak_freq': 3.0, 'peak_power': 50.0},
                'confidence': 0.8,
                'simple_summary': [
                    "RECOMMENDED ACTION: Increase P by 10% [Adjust first]",
                    "- Increase P by 10% to improve responsiveness."
                ]
            }
        }
    
    def _create_mock_recommendation_text(self):
        """Create mock recommendation text for testing"""
        return {
            'roll': [
                "Good tracking performance",
                "Current tune appears to be well-balanced based on basic metrics.",
                "High-frequency resonance detected: Consider reducing D by ~5%",
                "Recommendation confidence: 80% (High - based on comprehensive analysis)"
            ],
            'pitch': [
                "Good tracking performance",
                "Current tune appears to be well-balanced based on basic metrics.",
                "High-frequency resonance detected: Consider reducing D by ~5%",
                "Recommendation confidence: 80% (High - based on comprehensive analysis)"
            ],
            'yaw': [
                "Good tracking performance",
                "High phase margin (90.5°): System is overdamped, consider increasing P by ~10% for better responsiveness",
                "Low system overshoot (0.0%): Consider increasing P by ~5% for better responsiveness",
                "Slow system response (rise time: 25.0 samples): Consider increasing P by ~25%",
                "Moderate system settling (settling time: 40.0 samples): Consider increasing I by ~10%",
                "Recommendation confidence: 80% (High - based on comprehensive analysis)"
            ]
        }
    
    def _create_mock_segment_plots(self):
        """Create mock segment plots for testing"""
        # Create a tiny blank image encoded in base64 for testing
        blank_image = np.zeros((10, 10, 3), dtype=np.uint8)
        _, buffer = tempfile.mkstemp(suffix='.png')
        import matplotlib.pyplot as plt
        plt.imsave(buffer, blank_image)
        with open(buffer, 'rb') as f:
            image_data = f.read()
        os.remove(buffer)
        base64_image = base64.b64encode(image_data).decode('utf-8')
        
        return {
            '0_roll': {
                'time_domain': base64_image,
                'psd': base64_image
            },
            '0_pitch': {
                'time_domain': base64_image,
                'psd': base64_image
            },
            '0_yaw': {
                'time_domain': base64_image,
                'psd': base64_image
            }
        }
    
    def _create_mock_advanced_results(self):
        """Create mock advanced analysis results for testing"""
        return {
            '0_roll': {
                'transfer_function': {
                    'frequencies': np.linspace(0, 50, 100),
                    'magnitude': np.random.random(100),
                    'phase': np.random.random(100) * -180,
                    'coherence': np.random.random(100),
                    'phase_margin': 80.0,
                    'resonant_frequencies': [(15, 2.0), (30, 1.5)]
                },
                'arx_model': {
                    'fit': 80.0,
                    'step_response': np.cumsum(np.random.random(100))
                },
                'performance': {
                    'tracking_score': 85,
                    'noise_score': 70,
                    'response_score': 80,
                    'performance_index': 78
                }
            },
            '0_pitch': {
                'transfer_function': {
                    'frequencies': np.linspace(0, 50, 100),
                    'magnitude': np.random.random(100),
                    'phase': np.random.random(100) * -180,
                    'coherence': np.random.random(100),
                    'phase_margin': 75.0,
                    'resonant_frequencies': [(15, 2.0), (30, 1.5)]
                },
                'arx_model': {
                    'fit': 75.0,
                    'step_response': np.cumsum(np.random.random(100))
                },
                'performance': {
                    'tracking_score': 80,
                    'noise_score': 70,
                    'response_score': 75,
                    'performance_index': 75
                }
            },
            '0_yaw': {
                'transfer_function': {
                    'frequencies': np.linspace(0, 50, 100),
                    'magnitude': np.random.random(100),
                    'phase': np.random.random(100) * -180,
                    'coherence': np.random.random(100),
                    'phase_margin': 90.5,
                    'resonant_frequencies': [(15, 2.0), (30, 1.5)]
                },
                'arx_model': {
                    'fit': 70.0,
                    'step_response': np.cumsum(np.random.random(100))
                },
                'performance': {
                    'tracking_score': 70,
                    'noise_score': 75,
                    'response_score': 65,
                    'performance_index': 70
                }
            }
        }
    
    def _create_mock_advanced_plots(self):
        """Create mock advanced plots for testing"""
        # Create a tiny blank image encoded in base64 for testing
        blank_image = np.zeros((10, 10, 3), dtype=np.uint8)
        _, buffer = tempfile.mkstemp(suffix='.png')
        import matplotlib.pyplot as plt
        plt.imsave(buffer, blank_image)
        with open(buffer, 'rb') as f:
            image_data = f.read()
        os.remove(buffer)
        base64_image = base64.b64encode(image_data).decode('utf-8')
        
        return {
            '0_roll': {
                'transfer_function': base64_image,
                'arx_model': base64_image,
                'wavelet': base64_image,
                'performance': base64_image
            },
            '0_pitch': {
                'transfer_function': base64_image,
                'arx_model': base64_image,
                'wavelet': base64_image,
                'performance': base64_image
            },
            '0_yaw': {
                'transfer_function': base64_image,
                'arx_model': base64_image,
                'wavelet': base64_image,
                'performance': base64_image
            }
        }
    
    def test_generate_report_creates_file(self):
        """Test that generate_report creates a file with the expected name"""
        # Call generate_report with mock data
        report_path = self.reporter.generate_report(
            self.mock_analysis_results,
            self.mock_recommendations,
            self.mock_recommendations_text,
            self.mock_segment_plots,
            self.mock_advanced_results,
            self.mock_advanced_plots
        )
        
        # Check that the file was created
        self.assertTrue(os.path.exists(report_path))
        
        # Check that the file has content
        with open(report_path, 'r') as f:
            content = f.read()
        self.assertGreater(len(content), 0)
    
    def test_report_contains_recommendations(self):
        """Test that the generated report contains recommendations"""
        # Call generate_report with mock data
        report_path = self.reporter.generate_report(
            self.mock_analysis_results,
            self.mock_recommendations,
            self.mock_recommendations_text,
            self.mock_segment_plots,
            self.mock_advanced_results,
            self.mock_advanced_plots
        )
        
        # Read the content of the file
        with open(report_path, 'r') as f:
            content = f.read()
        
        # Check that the content contains recommendations
        self.assertIn("ROLL Axis", content)
        self.assertIn("PITCH Axis", content)
        self.assertIn("YAW Axis", content)
        self.assertIn("P: +0%", content)  # Roll and Pitch P adjustment
        self.assertIn("P: +10%", content)  # Yaw P adjustment
        self.assertIn("D: -5%", content)  # D adjustment for all axes
    
    def test_report_contains_detailed_explanations(self):
        """Test that the report contains detailed explanations for recommendations"""
        # Call generate_report with mock data
        report_path = self.reporter.generate_report(
            self.mock_analysis_results,
            self.mock_recommendations,
            self.mock_recommendations_text,
            self.mock_segment_plots,
            self.mock_advanced_results,
            self.mock_advanced_plots
        )
        
        # Read the content of the file
        with open(report_path, 'r') as f:
            content = f.read()
        
        # Check for detailed explanations for YAW axis
        self.assertIn("Why This Change Is Recommended", content)
        self.assertIn("High phase margin", content)
        
        # Check for well-tuned explanations for ROLL and PITCH
        self.assertIn("Well Tuned", content)
        self.assertIn("Low tracking error", content)
    
    def test_report_contains_step_response_sections(self):
        """Test that the report contains step response sections for each axis"""
        # Call generate_report with mock data
        report_path = self.reporter.generate_report(
            self.mock_analysis_results,
            self.mock_recommendations,
            self.mock_recommendations_text,
            self.mock_segment_plots,
            self.mock_advanced_results,
            self.mock_advanced_plots
        )
        
        # Read the content of the file
        with open(report_path, 'r') as f:
            content = f.read()
        
        # Check for step response sections
        self.assertIn("Step Response Analysis", content)
        self.assertIn("step response", content.lower())
        
    def test_report_without_advanced_data(self):
        """Test that the report still generates without advanced data"""
        # Call generate_report with basic data only
        report_path = self.reporter.generate_report(
            self.mock_analysis_results,
            self.mock_recommendations,
            self.mock_recommendations_text,
            self.mock_segment_plots
        )
        
        # Read the content of the file
        with open(report_path, 'r') as f:
            content = f.read()
        
        # Check that the report still contains basic recommendations
        self.assertIn("ROLL Axis", content)
        self.assertIn("PITCH Axis", content)
        self.assertIn("YAW Axis", content)
        
        # Make sure it doesn't crash due to missing advanced data
        self.assertGreater(len(content), 0)

if __name__ == '__main__':
    unittest.main() 