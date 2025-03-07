"""
Module for reading and decoding Betaflight log files
"""
import os
import subprocess
import pandas as pd
import numpy as np

class BlackboxLogReader:
    """Class for reading and decoding Betaflight blackbox logs"""
    
    def __init__(self, blackbox_decode_path=None):
        """
        Initialize the log reader
        
        Args:
            blackbox_decode_path: Path to the blackbox_decode executable
        """
        self.blackbox_decode_path = blackbox_decode_path
        
        # Try to find blackbox_decode if path not provided
        if not self.blackbox_decode_path:
            # Common locations
            common_paths = [
                '/usr/local/bin/blackbox_decode',
                '/usr/bin/blackbox_decode',
                os.path.expanduser('~/github/blackbox-tools/obj/blackbox_decode')
            ]
            
            for path in common_paths:
                if os.path.exists(path):
                    self.blackbox_decode_path = path
                    break
                    
        if not self.blackbox_decode_path or not os.path.exists(self.blackbox_decode_path):
            print("Warning: blackbox_decode not found. Please specify the path.")
    
    def decode_log(self, file_path):
        """
        Decode a Betaflight blackbox log using blackbox_decode.
        Returns the path to the decoded CSV file.
        
        Args:
            file_path: Path to the blackbox log file
            
        Returns:
            Path to the decoded CSV file or None if decoding failed
        """
        try:
            # Get the directory and filename
            log_dir = os.path.dirname(file_path)
            log_basename = os.path.basename(file_path)
            
            # Create the output directory
            output_dir = os.path.join(log_dir, "csv")
            os.makedirs(output_dir, exist_ok=True)
            
            # Run blackbox_decode with the full path
            print(f"Decoding log file: {file_path}")
            print(f"Using blackbox_decode from: {self.blackbox_decode_path}")
            
            result = subprocess.run(
                [self.blackbox_decode_path, "--stdout", file_path],
                capture_output=True,
                text=True
            )
            
            # Check if the command was successful
            if result.returncode != 0:
                print(f"Error decoding log: {result.stderr}")
                return None
            
            # Save the output to a CSV file
            csv_path = os.path.join(output_dir, log_basename + ".csv")
            with open(csv_path, 'w') as f:
                f.write(result.stdout)
            
            print(f"Decoded log saved to: {csv_path}")
            return csv_path
        
        except Exception as e:
            print(f"Error decoding log: {e}")
            return None
    
    def read_log(self, file_path):
        """
        Read a Betaflight blackbox log and return a pandas DataFrame.
        Handles both raw logs and pre-decoded CSV files.
        
        Args:
            file_path: Path to the log file or CSV file
            
        Returns:
            DataFrame containing the log data or None if reading failed
        """
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                print(f"File not found: {file_path}")
                return None
            
            # Check if it's a CSV file
            if file_path.lower().endswith('.csv'):
                df = pd.read_csv(file_path, low_memory=False)
            else:
                # Try to decode the log file
                csv_path = self.decode_log(file_path)
                if csv_path is None:
                    return None
                
                # Read the CSV file
                df = pd.read_csv(csv_path, low_memory=False)
            
            # Map column names
            column_mapping = {
                'loopIteration': 'loopIteration',
                ' time (us)': 'time',
                ' axisP[0]': 'P_roll',
                ' axisP[1]': 'P_pitch',
                ' axisP[2]': 'P_yaw',
                ' axisI[0]': 'I_roll',
                ' axisI[1]': 'I_pitch',
                ' axisI[2]': 'I_yaw',
                ' axisD[0]': 'D_roll',
                ' axisD[1]': 'D_pitch',
                ' axisF[0]': 'F_roll',
                ' axisF[1]': 'F_pitch',
                ' axisF[2]': 'F_yaw',
                ' rcCommand[0]': 'rc_roll',
                ' rcCommand[1]': 'rc_pitch',
                ' rcCommand[2]': 'rc_yaw',
                ' rcCommand[3]': 'rc_throttle',
                ' setpoint[0]': 'setpoint_roll',
                ' setpoint[1]': 'setpoint_pitch',
                ' setpoint[2]': 'setpoint_yaw',
                ' gyroADC[0]': 'gyro_roll',
                ' gyroADC[1]': 'gyro_pitch',
                ' gyroADC[2]': 'gyro_yaw'
            }
            
            # Rename columns that exist in the DataFrame
            for old_name, new_name in column_mapping.items():
                if old_name in df.columns:
                    df = df.rename(columns={old_name: new_name})
            
            # Convert time to seconds
            if 'time' in df.columns:
                df['time'] = (df['time'] - df['time'].iloc[0]) / 1000000.0
            
            return df
        
        except Exception as e:
            print(f"Error reading log file: {e}")
            return None 