# Betaflight Log Analyzer

A comprehensive tool for analyzing Betaflight blackbox logs and providing PID tuning recommendations based on advanced control theory techniques.

## Overview

The Betaflight Log Analyzer is a Python-based tool that helps pilots optimize their drone's flight performance by analyzing blackbox logs. It uses a combination of basic metrics, frequency analysis, and advanced control system techniques to generate data-driven PID tuning recommendations.

Key features:
- Automatic detection of flight segments
- Step response analysis for PID tuning
- Transfer function estimation
- ARX (AutoRegressive with eXogenous input) modeling
- Wavelet analysis for time-frequency insights
- Performance metrics calculation
- Clear, actionable tuning recommendations

## Installation

### Prerequisites

- Python 3.7 or higher
- [Betaflight Blackbox Tools](https://github.com/betaflight/blackbox-tools) for decoding logs

### Installing Blackbox Tools

1. Clone the repository:
   ```bash
   git clone https://github.com/betaflight/blackbox-tools.git
   cd blackbox-tools
   ```

2. Compile the tools:
   ```bash
   make
   ```

3. Make note of the path to the `blackbox_decode` executable. Typically, this will be:
   ```
   /path/to/blackbox-tools/obj/blackbox_decode
   ```

### Installing Betaflight Log Analyzer

1. Clone this repository:
   ```bash
   git clone https://github.com/yurynix/betaflight-log-analyzer.git
   cd betaflight-log-analyzer
   ```

2. Install the required Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

By default, the analyzer will look for the `blackbox_decode` executable in common installation locations. If your installation is in a custom location, you can specify it when running the tool or configure it in the source code.

To override the default path when running the tool:
```bash
python pid_analyzer.py --decode-path /path/to/blackbox-tools/obj/blackbox_decode /path/to/your/LOG00001.BFL
```

## Usage

### Basic Usage

Analyze a log file and get PID tuning recommendations:
```bash
python pid_analyzer.py /path/to/your/LOG00001.BFL
```

### Advanced Analysis

For more detailed analysis including transfer functions, ARX modeling, wavelet analysis, and performance metrics:
```bash
python pid_analyzer.py --advanced /path/to/your/LOG00001.BFL
```

### Options

```
--help                Show help message and exit
--advanced            Perform advanced analysis (transfer function, ARX modeling, etc.)
--decode-path PATH    Path to blackbox_decode executable
--output-dir DIR      Directory to save analysis files (default: <log_directory>/<log_name>_analysis)
--no-plots            Skip generating plots (faster analysis)
```

## Analysis Methods

The Betaflight Log Analyzer uses several techniques to analyze flight performance:

### Basic Analysis

- **Step Response Analysis**: Identifies how the drone responds to rapid changes in setpoint
- **Tracking Error Metrics**: Measures how well the gyro follows the setpoint
- **Frequency Domain Analysis**: Identifies oscillations and resonances

### Advanced Analysis

- **Transfer Function Estimation**: Models the drone's frequency response
- **ARX Modeling**: Creates a mathematical model of your drone's behavior
- **Wavelet Analysis**: Detects time-varying oscillations across different frequency bands
- **Performance Index**: Computes comprehensive performance metrics

## Recommendations

Based on the analysis, the tool provides recommendations for adjusting PID values. Recommendations include:

1. **What to Change**: Specific PID term adjustments (P, I, or D) with exact percentages
2. **What to Change First**: Prioritized recommendations to tackle the most significant issues first
3. **Why to Change**: Detailed explanations of the analysis that led to each recommendation

The recommendations are customized for each axis (Roll, Pitch, and Yaw) based on its specific characteristics.

### Understanding the Recommendations

The PID recommendations are based on multiple factors:

- **P-term** (Proportional):
  - Increased when response is too slow or phase margin is high (overdamped system)
  - Decreased when oscillations or resonances are detected

- **I-term** (Integral):
  - Increased when persistent errors or slow settling time is detected
  - Decreased when low-frequency oscillations are present

- **D-term** (Derivative):
  - Increased when mid-frequency oscillations need additional damping
  - Decreased when high-frequency noise is detected

## Output

The analyzer generates multiple outputs:

1. **Command Line Summary**: A concise overview of the findings and recommendations
2. **HTML Report**: A detailed report with visualizations and explanations
3. **Plot Files**: PNG images of all generated plots for further inspection
4. **Processed Data**: CSV files with the analyzed data

## Development

### Running Tests

```bash
python run_tests.py
```

### Code Structure

- `betaflight_log_analyzer/`: Main package
  - `analysis/`: Analysis modules (PID, segment, frequency, etc.)
  - `data/`: Data handling modules
  - `reports/`: Report generation
  - `visualization/`: Plotting and visualization
- `tests/`: Unit tests
- `pid_analyzer.py`: Main entry point

## Troubleshooting

If you encounter issues with Blackbox log decoding:
1. Ensure the blackbox-tools are correctly compiled
2. Verify the path to blackbox_decode is correct
3. Check that your log files are valid Betaflight blackbox logs (.BFL or .BBL format)

## Acknowledgements

- The Betaflight Team for creating the underlying firmware and blackbox tools
- The FPV community for their insights on PID tuning

## License

[MIT License](LICENSE) 