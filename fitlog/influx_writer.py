#!/usr/bin/env python3
"""
Module responsible for writing data to InfluxDB
"""

import logging
import os
from datetime import datetime
from typing import Dict, List, Optional

from dotenv import load_dotenv
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

# Load environment variables
load_dotenv()

# Log configuration
logger = logging.getLogger(__name__)


class InfluxWriter:
    """Class for writing data to InfluxDB"""

    def __init__(self):
        self.url = os.getenv("INFLUXDB_URL", "http://localhost:8086")
        self.token = os.getenv("INFLUXDB_ADMIN_TOKEN")
        self.org = os.getenv("INFLUXDB_ORG", "fitlog")
        self.bucket = os.getenv("INFLUXDB_BUCKET", "health_data")

        if not self.token:
            raise ValueError("INFLUXDB_ADMIN_TOKEN environment variable is not set")

        self.client = InfluxDBClient(url=self.url, token=self.token, org=self.org)

        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)

        logger.info(f"InfluxDB connection initialized: {self.url}")

    def __del__(self):
        """Close client in destructor"""
        if hasattr(self, "client"):
            self.client.close()

    def create_point(
        self,
        measurement: str,
        value: float,
        timestamp: int,
        tags: Optional[Dict] = None,
        fields: Optional[Dict] = None,
    ) -> Point:
        """Create InfluxDB Point object"""
        point = Point(measurement)

        # Add tags
        if tags:
            for key, val in tags.items():
                point.tag(key, val)

        # Add main value
        point.field("value", value)

        # Add additional fields
        if fields:
            for key, val in fields.items():
                point.field(key, val)

        # Set timestamp (convert from seconds to nanoseconds)
        point.time(timestamp * 1000000000)

        return point

    def write_health_data(self, data: List[Dict]) -> int:
        """Write health data to InfluxDB"""
        if not data:
            return 0

        points = []

        for item in data:
            measurement = item.get("measurement")
            value = item.get("value")
            timestamp = item.get("timestamp")

            if not all([measurement, value is not None, timestamp]):
                logger.warning(f"Skipping incomplete data: {item}")
                continue

            # Processing by measurement type
            if measurement == "steps":
                point = self.create_point(
                    measurement="steps",
                    value=int(value),
                    timestamp=timestamp,
                    tags={"unit": "count"},
                )

            elif measurement == "calories":
                point = self.create_point(
                    measurement="calories",
                    value=float(value),
                    timestamp=timestamp,
                    tags={"unit": "kcal"},
                )

            elif measurement == "weight":
                point = self.create_point(
                    measurement="weight",
                    value=float(value),
                    timestamp=timestamp,
                    tags={"unit": "kg"},
                )

            elif measurement == "heart_rate":
                point = self.create_point(
                    measurement="heart_rate",
                    value=float(value),
                    timestamp=timestamp,
                    tags={"unit": "bpm"},
                )

            elif measurement == "sleep":
                # Sleep data requires special processing
                sleep_type = item.get("sleep_type", 0)
                sleep_type_name = self.get_sleep_type_name(sleep_type)

                point = self.create_point(
                    measurement="sleep",
                    value=float(value),  # Sleep duration (seconds)
                    timestamp=timestamp,
                    tags={"unit": "seconds", "sleep_type": sleep_type_name},
                    fields={
                        "sleep_type_code": sleep_type,
                        "duration_minutes": float(value) / 60,
                        "duration_hours": float(value) / 3600,
                    },
                )

            else:
                logger.warning(f"Unknown measurement type: {measurement}")
                continue

            points.append(point)

        # Write data
        if points:
            try:
                self.write_api.write(bucket=self.bucket, record=points)
                logger.info(f"Successfully wrote {len(points)} data points to InfluxDB")
                return len(points)
            except Exception as e:
                logger.error(f"InfluxDB write error: {e}")
                raise

        return 0

    def get_sleep_type_name(self, sleep_type: int) -> str:
        """Get sleep type name from sleep type code"""
        sleep_types = {
            1: "awake",
            2: "sleep",
            3: "out_of_bed",
            4: "light_sleep",
            5: "deep_sleep",
            6: "rem_sleep",
        }
        return sleep_types.get(sleep_type, "unknown")

    def write_steps_data(self, steps_data: List[Dict]) -> int:
        """Write steps data"""
        return self.write_health_data(
            [
                {
                    "measurement": "steps",
                    "value": item["value"],
                    "timestamp": item["timestamp"],
                }
                for item in steps_data
            ]
        )

    def write_weight_data(self, weight_data: List[Dict]) -> int:
        """Write weight data"""
        return self.write_health_data(
            [
                {
                    "measurement": "weight",
                    "value": item["value"],
                    "timestamp": item["timestamp"],
                }
                for item in weight_data
            ]
        )

    def write_calories_data(self, calories_data: List[Dict]) -> int:
        """Write calories data"""
        return self.write_health_data(
            [
                {
                    "measurement": "calories",
                    "value": item["value"],
                    "timestamp": item["timestamp"],
                }
                for item in calories_data
            ]
        )

    def write_heart_rate_data(self, heart_rate_data: List[Dict]) -> int:
        """Write heart rate data"""
        return self.write_health_data(
            [
                {
                    "measurement": "heart_rate",
                    "value": item["value"],
                    "timestamp": item["timestamp"],
                }
                for item in heart_rate_data
            ]
        )

    def write_sleep_data(self, sleep_data: List[Dict]) -> int:
        """Write sleep data"""
        return self.write_health_data(
            [
                {
                    "measurement": "sleep",
                    "value": item["value"],
                    "timestamp": item["timestamp"],
                    "sleep_type": item.get("sleep_type", 0),
                }
                for item in sleep_data
            ]
        )

    def test_connection(self) -> bool:
        """Test connection to InfluxDB"""
        try:
            # Execute simple query to verify connection
            query_api = self.client.query_api()
            query = f'from(bucket: "{self.bucket}") |> range(start: -1m) |> limit(n: 1)'

            query_api.query(query)
            return True

        except Exception as e:
            logger.error(f"InfluxDB connection test error: {e}")
            return False

    def get_latest_data(self, measurement: str, limit: int = 10) -> List[Dict]:
        """Get latest data for specified measurement"""
        try:
            query_api = self.client.query_api()
            query = f"""
                from(bucket: "{self.bucket}")
                |> range(start: -30d)
                |> filter(fn: (r) => r._measurement == "{measurement}")
                |> sort(columns: ["_time"], desc: true)
                |> limit(n: {limit})
            """

            result = query_api.query(query)

            data = []
            for table in result:
                for record in table.records:
                    data.append(
                        {
                            "time": record.get_time(),
                            "value": record.get_value(),
                            "measurement": record.get_measurement(),
                        }
                    )

            return data

        except Exception as e:
            logger.error(f"Data retrieval error: {e}")
            return []


def main():
    """Main function for test execution"""
    try:
        writer = InfluxWriter()

        # Connection test
        if writer.test_connection():
            print("InfluxDB connection successful")
        else:
            print("InfluxDB connection failed")
            return

        # Write test data
        test_data = [
            {
                "measurement": "steps",
                "value": 8500,
                "timestamp": int(datetime.now().timestamp()),
            }
        ]

        points_written = writer.write_health_data(test_data)
        print(f"Test data write completed: {points_written} items")

        # Get latest data
        latest_steps = writer.get_latest_data("steps", 5)
        print(f"Latest steps data: {len(latest_steps)} items")

    except Exception as e:
        logger.error(f"Test execution error: {e}")


if __name__ == "__main__":
    main()
