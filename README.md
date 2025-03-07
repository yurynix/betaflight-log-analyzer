# Betaflight Log Analyzer

A tool for analyzing Betaflight blackbox logs and providing PID tuning recommendations.

## Features

- Automatic decoding of Betaflight blackbox logs
- Identification of active flight segments
- Analysis of flight performance:
  - Time domain analysis of tracking performance
  - Frequency domain analysis for oscillation detection
  - Error metrics calculation
- PID tuning recommendations:
  - Specific adjustments for P, I, and D terms
  - Detailed reasoning for each recommendation
- Comprehensive HTML report generation:
  - Interactive navigation
  - High-quality visualizations
  - Detailed statistics for each flight segment
  - Integrated tuning guide
- Advanced analysis techniques (optional):
  - Transfer function estimation
  - System identification using ARX models
  - Time-frequency analysis using wavelets
  - Comprehensive performance index

## Installation

### Requirements

- Python 3.8 or newer
- `blackbox_decode` executable from the [Blackbox Tools](https://github.com/betaflight/blackbox-tools) repository

### Installing from Source

```bash
git clone https://github.com/yourusername/betaflight-log-analyzer.git
cd betaflight-log-analyzer
pip install -e .
```

## Usage

### Basic Usage

```bash
betaflight-log-analyzer /path/to/your/LOG00001.BFL
```

### Advanced Options

```bash
betaflight-log-analyzer /path/to/your/LOG00001.BFL \
    --blackbox-decode /path/to/blackbox_decode \
    --throttle-threshold 1500 \
    --output-dir /path/to/output
```

### Command Line Arguments

- `log_file`: Path to the blackbox log file (required)
- `--blackbox-decode`: Path to the blackbox_decode executable (optional, will try to find automatically)
- `--throttle-threshold`: Throttle value above which flight is considered active (default: 1300)
- `--output-dir`: Directory to save report and plots (default: creates a directory named after the log file)
- `--advanced`: Enable advanced analysis techniques (transfer function, ARX modeling, etc.)
- `--skip-wavelet`: Skip wavelet analysis when using advanced mode (can be computationally intensive)

## Understanding the Reports

### Time Domain Analysis

The time domain graphs show:
- Blue line: Setpoint (what your drone is trying to do)
- Red line: Gyro (what your drone actually did)
- Green line: Error (difference between setpoint and gyro)

Good tuning shows minimal error and prompt response to setpoint changes.

### Frequency Domain Analysis

The frequency domain graphs show:
- Green area (0-10Hz): Low frequency oscillations (often related to P and I term issues)
- Orange area (10-30Hz): Mid frequency oscillations (often related to P term)
- Red area (>30Hz): High frequency oscillations (often related to D term and noise issues)

A well-tuned drone typically shows a smooth curve with no sharp peaks.

### Advanced Analysis

The advanced analysis mode offers sophisticated techniques for deeper insights:

#### Transfer Function Analysis
Shows frequency response characteristics of your drone using:
- Magnitude plot: How much your drone amplifies signals at different frequencies
- Phase plot: Time delay between input and output
- Coherence plot: How linearly related input and output are

#### ARX Model Identification
Creates a mathematical model of your drone's behavior:
- Predicts how your drone responds to inputs
- Shows theoretical step response
- Calculates fit quality (how well the model matches reality)

#### Wavelet Analysis
Detects time-varying oscillations across frequency bands:
- Scalogram: Shows power at different frequencies over time
- Dominant frequency tracking: Shows how frequency content changes
- Highlights problematic frequency regions

#### Performance Index
Provides a comprehensive scoring system for handling characteristics:
- Tracking score: How well gyro follows setpoint
- Noise reduction: How well high-frequency noise is suppressed
- Responsiveness: How quickly your drone responds to inputs

To use these features, add the `--advanced` flag:

```bash
betaflight-log-analyzer /path/to/your/LOG00001.BFL --advanced
```

## Project Structure

```
betaflight_log_analyzer/
├── __init__.py
├── __main__.py
├── main.py
├── utils/
│   ├── __init__.py
│   └── log_reader.py
├── analysis/
│   ├── __init__.py
│   ├── segment_analyzer.py
│   ├── pid_recommender.py
│   └── advanced_analysis.py
├── visualization/
│   ├── __init__.py
│   ├── plots.py
│   └── advanced_plots.py
└── reports/
    ├── __init__.py
    └── html_reporter.py
```

## License

MIT 