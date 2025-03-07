# Betaflight PID Analyzer

This program analyzes Betaflight blackbox logs to help tune your drone's PID values by analyzing step responses.

## Requirements

- Python 3.7 or higher
- Required Python packages (install using `pip install -r requirements.txt`):
  - numpy
  - pandas
  - matplotlib
  - scipy

## Installation

1. Clone this repository
2. Install the required packages:
```bash
pip install -r requirements.txt
```

## Usage

Run the program with your Betaflight blackbox log file as an argument:

```bash
python pid_analyzer.py your_blackbox_log.csv
```

The program will:
1. Read and analyze your blackbox log
2. Identify step responses in the data
3. Calculate system characteristics (rise time, overshoot, settling time)
4. Generate PID tuning recommendations
5. Create a visualization of the step responses (saved as 'step_responses.png')

## Output

The program will provide:
- Analysis results including average rise time, overshoot, and settling time
- PID tuning recommendations based on the analysis
- A plot showing the step responses (saved as 'step_responses.png')

## Notes

- The program assumes the blackbox log is in CSV format
- The analysis looks for significant changes in setpoint to identify step responses
- PID recommendations are based on general guidelines and may need adjustment for your specific setup
- The visualization helps you understand the system's response characteristics 