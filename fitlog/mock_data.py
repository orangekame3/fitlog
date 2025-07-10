#!/usr/bin/env python3
"""
Mock data generator for fitlog demonstration
Generates realistic health data without requiring Google Fit API authentication
"""

import random
import logging
from datetime import datetime, timedelta
from typing import List, Dict

import click
import pytz
from dotenv import load_dotenv

from influx_writer import InfluxWriter

# Load environment variables
load_dotenv()

# Log configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MockDataGenerator:
    """Mock health data generator for demonstration purposes"""
    
    def __init__(self, timezone_str: str = 'Asia/Tokyo'):
        self.timezone = pytz.timezone(timezone_str)
        
    def generate_steps_data(self, days: int = 7) -> List[Dict]:
        """Generate mock step count data"""
        data = []
        now = datetime.now(self.timezone)
        
        for day in range(days):
            # Generate data for each hour of the day
            day_start = now - timedelta(days=day)
            day_start = day_start.replace(hour=6, minute=0, second=0, microsecond=0)
            
            daily_steps = 0
            hourly_base_steps = random.randint(8000, 15000) // 18  # Spread over ~18 active hours
            
            for hour in range(18):  # 6 AM to 11 PM
                hour_time = day_start + timedelta(hours=hour)
                
                # More steps during active hours (morning, lunch, evening)
                if hour in [1, 2, 6, 7, 11, 12]:  # 7-8 AM, 12-1 PM, 5-6 PM
                    steps = int(hourly_base_steps * random.uniform(1.5, 2.5))
                elif hour in [0, 8, 9, 10, 13, 14, 15]:  # Normal activity
                    steps = int(hourly_base_steps * random.uniform(0.8, 1.2))
                else:  # Lower activity
                    steps = int(hourly_base_steps * random.uniform(0.3, 0.7))
                
                # Add some randomness
                steps += random.randint(-50, 100)
                steps = max(0, steps)
                daily_steps += steps
                
                data.append({
                    'measurement': 'steps',
                    'value': steps,
                    'timestamp': int(hour_time.timestamp())
                })
            
            logger.info(f"Generated {daily_steps} steps for {day_start.strftime('%Y-%m-%d')}")
        
        return data
    
    def generate_weight_data(self, days: int = 7) -> List[Dict]:
        """Generate mock weight data"""
        data = []
        now = datetime.now(self.timezone)
        
        # Base weight with slight variations
        base_weight = random.uniform(60.0, 80.0)
        
        for day in range(days):
            day_time = now - timedelta(days=day)
            # Weight measurements typically in the morning
            day_time = day_time.replace(hour=7, minute=random.randint(0, 30), second=0, microsecond=0)
            
            # Small daily variations
            weight_variation = random.uniform(-0.5, 0.5)
            weight = base_weight + weight_variation + (random.uniform(-0.1, 0.1) * day)
            weight = round(weight, 1)
            
            data.append({
                'measurement': 'weight',
                'value': weight,
                'timestamp': int(day_time.timestamp())
            })
        
        return data
    
    def generate_heart_rate_data(self, days: int = 7) -> List[Dict]:
        """Generate mock heart rate data"""
        data = []
        now = datetime.now(self.timezone)
        
        for day in range(days):
            day_start = now - timedelta(days=day)
            
            # Generate heart rate data every 30 minutes during active hours
            for hour in range(6, 23):  # 6 AM to 11 PM
                for minute in [0, 30]:
                    measure_time = day_start.replace(hour=hour, minute=minute, second=0, microsecond=0)
                    
                    # Base heart rate varies by time of day
                    if 6 <= hour <= 8:  # Morning
                        base_hr = random.randint(65, 85)
                    elif 9 <= hour <= 17:  # Daytime
                        base_hr = random.randint(70, 90)
                    elif 18 <= hour <= 20:  # Evening activity
                        base_hr = random.randint(80, 110)
                    else:  # Night
                        base_hr = random.randint(60, 75)
                    
                    # Add some randomness
                    heart_rate = base_hr + random.randint(-10, 15)
                    heart_rate = max(50, min(180, heart_rate))
                    
                    data.append({
                        'measurement': 'heart_rate',
                        'value': heart_rate,
                        'timestamp': int(measure_time.timestamp())
                    })
        
        return data
    
    def generate_sleep_data(self, days: int = 7) -> List[Dict]:
        """Generate mock sleep data"""
        data = []
        now = datetime.now(self.timezone)
        
        for day in range(days):
            # Sleep period: 11 PM to 7 AM next day
            sleep_start = now - timedelta(days=day)
            sleep_start = sleep_start.replace(hour=23, minute=random.randint(0, 30), second=0, microsecond=0)
            
            # Sleep duration: 6-9 hours
            sleep_duration_hours = random.uniform(6.5, 8.5)
            sleep_duration_seconds = int(sleep_duration_hours * 3600)
            
            # Deep sleep: 20-25% of total sleep
            deep_sleep_duration = int(sleep_duration_seconds * random.uniform(0.20, 0.25))
            
            # REM sleep: 20-25% of total sleep
            rem_sleep_duration = int(sleep_duration_seconds * random.uniform(0.20, 0.25))
            
            # Light sleep: remainder
            light_sleep_duration = sleep_duration_seconds - deep_sleep_duration - rem_sleep_duration
            
            # Create sleep segments
            current_time = sleep_start
            
            # Light sleep periods
            for i in range(3):  # Multiple light sleep periods
                segment_duration = light_sleep_duration // 3
                data.append({
                    'measurement': 'sleep',
                    'value': segment_duration,
                    'timestamp': int(current_time.timestamp()),
                    'sleep_type': 4  # Light sleep
                })
                current_time += timedelta(seconds=segment_duration)
            
            # Deep sleep period
            data.append({
                'measurement': 'sleep',
                'value': deep_sleep_duration,
                'timestamp': int(current_time.timestamp()),
                'sleep_type': 5  # Deep sleep
            })
            current_time += timedelta(seconds=deep_sleep_duration)
            
            # REM sleep period
            data.append({
                'measurement': 'sleep',
                'value': rem_sleep_duration,
                'timestamp': int(current_time.timestamp()),
                'sleep_type': 6  # REM sleep
            })
        
        return data
    
    def generate_calories_data(self, days: int = 7) -> List[Dict]:
        """Generate mock calorie consumption data"""
        data = []
        now = datetime.now(self.timezone)
        
        for day in range(days):
            day_start = now - timedelta(days=day)
            
            # Generate calorie data every 2 hours during active time
            daily_calories = 0
            
            for hour in range(6, 23, 2):  # Every 2 hours from 6 AM to 11 PM
                measure_time = day_start.replace(hour=hour, minute=0, second=0, microsecond=0)
                
                # Calorie burn varies by time (higher during activity periods)
                if hour in [7, 12, 18]:  # Meal/activity times
                    calories = random.randint(150, 300)
                elif hour in [8, 9, 13, 14, 19, 20]:  # Active periods
                    calories = random.randint(100, 200)
                else:  # Rest periods
                    calories = random.randint(50, 120)
                
                daily_calories += calories
                
                data.append({
                    'measurement': 'calories',
                    'value': calories,
                    'timestamp': int(measure_time.timestamp())
                })
            
            logger.info(f"Generated {daily_calories} calories for {day_start.strftime('%Y-%m-%d')}")
        
        return data
    
    def generate_all_mock_data(self, days: int = 7) -> Dict[str, List[Dict]]:
        """Generate all types of mock health data"""
        logger.info(f"Generating mock health data for {days} days")
        
        return {
            'steps': self.generate_steps_data(days),
            'weight': self.generate_weight_data(days),
            'heart_rate': self.generate_heart_rate_data(days),
            'sleep': self.generate_sleep_data(days),
            'calories': self.generate_calories_data(days)
        }


@click.command()
@click.option('--days', default=7, help='Number of days of mock data to generate')
@click.option('--dry-run', is_flag=True, help='Show generated data without writing to database')
def main(days: int, dry_run: bool):
    """Generate mock health data for demonstration purposes"""
    try:
        # Generate mock data
        generator = MockDataGenerator()
        all_data = generator.generate_all_mock_data(days)
        
        if dry_run:
            logger.info("DRY RUN MODE: Generated mock data (not writing to database)")
            for data_type, data in all_data.items():
                logger.info(f"{data_type}: {len(data)} data points")
            return
        
        # Write to InfluxDB
        influx_writer = InfluxWriter()
        
        total_points = 0
        for data_type, data in all_data.items():
            if data:
                points_written = influx_writer.write_health_data(data)
                total_points += points_written
                logger.info(f"{data_type}: {points_written} points written to InfluxDB")
        
        logger.info(f"Successfully wrote {total_points} mock data points to InfluxDB")
        logger.info("Mock data generation completed! You can now view dashboards in Grafana.")
        
    except Exception as e:
        logger.error(f"Mock data generation failed: {e}")
        raise


if __name__ == '__main__':
    main()