#!/usr/bin/env python3
"""
Script to fetch health data from Google Fit API and store it in InfluxDB
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import click
import pytz
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from influx_writer import InfluxWriter

# Load environment variables
load_dotenv()

# Log configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Google Fit API scopes
SCOPES = [
    'https://www.googleapis.com/auth/fitness.activity.read',
    'https://www.googleapis.com/auth/fitness.body.read',
    'https://www.googleapis.com/auth/fitness.sleep.read',
    'https://www.googleapis.com/auth/fitness.heart_rate.read'
]

# Data source definitions
DATA_SOURCES = {
    'steps': 'derived:com.google.step_count.delta:com.google.android.gms:estimated_steps',
    'calories': 'derived:com.google.calories.expended:com.google.android.gms:merge_calories_expended',
    'distance': 'derived:com.google.distance.delta:com.google.android.gms:merge_distance_delta',
    'weight': 'derived:com.google.weight:com.google.android.gms:merge_weight',
    'heart_rate': 'derived:com.google.heart_rate.bpm:com.google.android.gms:merge_heart_rate_bpm',
    'sleep': 'derived:com.google.sleep.segment:com.google.android.gms:merged'
}

class GoogleFitClient:
    """Google Fit API client"""
    
    def __init__(self, credentials_path: str = 'auth/client_secret.json', 
                 token_path: str = 'auth/token.json'):
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.service = None
        self.timezone = pytz.timezone(os.getenv('TIMEZONE', 'Asia/Tokyo'))
        
    def authenticate(self) -> None:
        """Execute OAuth authentication"""
        creds = None
        
        # Check existing token file
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)
        
        # If no valid credentials, perform new authentication
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_path):
                    raise FileNotFoundError(f"Authentication file not found: {self.credentials_path}")
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save token
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())
        
        self.service = build('fitness', 'v1', credentials=creds)
        logger.info("Google Fit API authentication completed")
    
    def get_time_range(self, days_back: int = 1) -> tuple:
        """Calculate time range for data to fetch"""
        now = datetime.now(self.timezone)
        end_time = now.replace(hour=23, minute=59, second=59, microsecond=999999)
        start_time = end_time - timedelta(days=days_back)
        
        # Convert to nanoseconds
        start_ns = int(start_time.timestamp() * 1000000000)
        end_ns = int(end_time.timestamp() * 1000000000)
        
        return start_ns, end_ns
    
    def fetch_dataset(self, data_source: str, start_time: int, end_time: int) -> List[Dict]:
        """Fetch data from specified data source"""
        try:
            dataset_id = f"{start_time}-{end_time}"
            
            result = self.service.users().dataSources().datasets().get(
                userId='me',
                dataSourceId=data_source,
                datasetId=dataset_id
            ).execute()
            
            return result.get('point', [])
        
        except Exception as e:
            logger.error(f"Data fetch error ({data_source}): {e}")
            return []
    
    def fetch_steps(self, start_time: int, end_time: int) -> List[Dict]:
        """Fetch steps data"""
        points = self.fetch_dataset(DATA_SOURCES['steps'], start_time, end_time)
        
        steps_data = []
        for point in points:
            if point.get('value') and len(point['value']) > 0:
                timestamp = int(point['startTimeNanos']) // 1000000000
                steps = point['value'][0]['intVal']
                
                steps_data.append({
                    'measurement': 'steps',
                    'timestamp': timestamp,
                    'value': steps
                })
        
        return steps_data
    
    def fetch_calories(self, start_time: int, end_time: int) -> List[Dict]:
        """Fetch calorie consumption data"""
        points = self.fetch_dataset(DATA_SOURCES['calories'], start_time, end_time)
        
        calories_data = []
        for point in points:
            if point.get('value') and len(point['value']) > 0:
                timestamp = int(point['startTimeNanos']) // 1000000000
                calories = point['value'][0]['fpVal']
                
                calories_data.append({
                    'measurement': 'calories',
                    'timestamp': timestamp,
                    'value': calories
                })
        
        return calories_data
    
    def fetch_weight(self, start_time: int, end_time: int) -> List[Dict]:
        """Fetch weight data"""
        points = self.fetch_dataset(DATA_SOURCES['weight'], start_time, end_time)
        
        weight_data = []
        for point in points:
            if point.get('value') and len(point['value']) > 0:
                timestamp = int(point['startTimeNanos']) // 1000000000
                weight = point['value'][0]['fpVal']
                
                weight_data.append({
                    'measurement': 'weight',
                    'timestamp': timestamp,
                    'value': weight
                })
        
        return weight_data
    
    def fetch_heart_rate(self, start_time: int, end_time: int) -> List[Dict]:
        """Fetch heart rate data"""
        points = self.fetch_dataset(DATA_SOURCES['heart_rate'], start_time, end_time)
        
        heart_rate_data = []
        for point in points:
            if point.get('value') and len(point['value']) > 0:
                timestamp = int(point['startTimeNanos']) // 1000000000
                heart_rate = point['value'][0]['fpVal']
                
                heart_rate_data.append({
                    'measurement': 'heart_rate',
                    'timestamp': timestamp,
                    'value': heart_rate
                })
        
        return heart_rate_data
    
    def fetch_sleep(self, start_time: int, end_time: int) -> List[Dict]:
        """Fetch sleep data"""
        points = self.fetch_dataset(DATA_SOURCES['sleep'], start_time, end_time)
        
        sleep_data = []
        for point in points:
            if point.get('value') and len(point['value']) > 0:
                start_timestamp = int(point['startTimeNanos']) // 1000000000
                end_timestamp = int(point['endTimeNanos']) // 1000000000
                sleep_type = point['value'][0]['intVal']
                duration = end_timestamp - start_timestamp
                
                sleep_data.append({
                    'measurement': 'sleep',
                    'timestamp': start_timestamp,
                    'value': duration,
                    'sleep_type': sleep_type
                })
        
        return sleep_data
    
    def fetch_all_data(self, days_back: int = 1) -> Dict[str, List[Dict]]:
        """Fetch all health data"""
        if not self.service:
            self.authenticate()
        
        start_time, end_time = self.get_time_range(days_back)
        
        logger.info(f"Starting data fetch: from {days_back} days ago to present")
        
        all_data = {}
        
        # Fetch each data type
        data_fetchers = {
            'steps': self.fetch_steps,
            'calories': self.fetch_calories,
            'weight': self.fetch_weight,
            'heart_rate': self.fetch_heart_rate,
            'sleep': self.fetch_sleep
        }
        
        for data_type, fetcher in data_fetchers.items():
            try:
                data = fetcher(start_time, end_time)
                all_data[data_type] = data
                logger.info(f"{data_type}: fetched {len(data)} data points")
            except Exception as e:
                logger.error(f"{data_type} data fetch error: {e}")
                all_data[data_type] = []
        
        return all_data

@click.command()
@click.option('--days', default=1, help='Number of days to fetch (how many days back)')
@click.option('--dry-run', is_flag=True, help='Execute without writing to database')
def main(days: int, dry_run: bool):
    """Fetch data from Google Fit API and store in InfluxDB"""
    try:
        # Initialize Google Fit client
        fit_client = GoogleFitClient()
        
        # Fetch data
        all_data = fit_client.fetch_all_data(days)
        
        if dry_run:
            logger.info("Dry run mode: will not write to database")
            for data_type, data in all_data.items():
                logger.info(f"{data_type}: {len(data)} items")
            return
        
        # Write to InfluxDB
        influx_writer = InfluxWriter()
        
        total_points = 0
        for data_type, data in all_data.items():
            if data:
                points_written = influx_writer.write_health_data(data)
                total_points += points_written
                logger.info(f"{data_type}: wrote {points_written} items to InfluxDB")
        
        logger.info(f"Processing completed for total {total_points} data points")
        
    except Exception as e:
        logger.error(f"Execution error: {e}")
        raise

if __name__ == '__main__':
    main()