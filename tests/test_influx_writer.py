"""
InfluxDB書き込み機能のテスト
"""

import os
import unittest
from unittest.mock import Mock, patch

from fitlog.influx_writer import InfluxWriter


class TestInfluxWriter(unittest.TestCase):
    """InfluxWriterクラスのテスト"""

    def setUp(self):
        """テストの前処理"""
        self.test_env = {
            "INFLUXDB_URL": "http://localhost:8086",
            "INFLUXDB_ADMIN_TOKEN": "test_token",
            "INFLUXDB_ORG": "test_org",
            "INFLUXDB_BUCKET": "test_bucket",
        }

    @patch.dict(os.environ, {"INFLUXDB_ADMIN_TOKEN": "test_token"})
    @patch("fitlog.influx_writer.InfluxDBClient")
    def test_init(self, mock_client):
        """初期化のテスト"""
        writer = InfluxWriter()

        self.assertEqual(writer.url, "http://localhost:8086")
        self.assertEqual(writer.token, "test_token")
        self.assertEqual(writer.org, "fitlog")
        self.assertEqual(writer.bucket, "health_data")
        mock_client.assert_called_once()

    @patch.dict(os.environ, {})
    def test_init_without_token(self):
        """トークンなしの初期化エラーテスト"""
        with self.assertRaises(ValueError) as context:
            InfluxWriter()

        self.assertIn("INFLUXDB_ADMIN_TOKEN", str(context.exception))

    @patch.dict(os.environ, {"INFLUXDB_ADMIN_TOKEN": "test_token"})
    @patch("fitlog.influx_writer.InfluxDBClient")
    def test_create_point(self, mock_client):
        """Pointオブジェクト作成のテスト"""
        writer = InfluxWriter()

        point = writer.create_point(
            measurement="test_measurement",
            value=100.0,
            timestamp=1234567890,
            tags={"tag1": "value1"},
            fields={"field1": "value1"},
        )

        self.assertIsNotNone(point)

    @patch.dict(os.environ, {"INFLUXDB_ADMIN_TOKEN": "test_token"})
    @patch("fitlog.influx_writer.InfluxDBClient")
    def test_write_steps_data(self, mock_client):
        """歩数データ書き込みのテスト"""
        mock_write_api = Mock()
        mock_client.return_value.write_api.return_value = mock_write_api

        writer = InfluxWriter()

        test_data = [
            {"measurement": "steps", "value": 1000, "timestamp": 1234567890},
            {"measurement": "steps", "value": 2000, "timestamp": 1234567891},
        ]

        result = writer.write_health_data(test_data)

        self.assertEqual(result, 2)
        mock_write_api.write.assert_called_once()

    @patch.dict(os.environ, {"INFLUXDB_ADMIN_TOKEN": "test_token"})
    @patch("fitlog.influx_writer.InfluxDBClient")
    def test_write_empty_data(self, mock_client):
        """空データ書き込みのテスト"""
        writer = InfluxWriter()

        result = writer.write_health_data([])

        self.assertEqual(result, 0)

    @patch.dict(os.environ, {"INFLUXDB_ADMIN_TOKEN": "test_token"})
    @patch("fitlog.influx_writer.InfluxDBClient")
    def test_get_sleep_type_name(self, mock_client):
        """睡眠タイプ名取得のテスト"""
        writer = InfluxWriter()

        self.assertEqual(writer.get_sleep_type_name(1), "awake")
        self.assertEqual(writer.get_sleep_type_name(2), "sleep")
        self.assertEqual(writer.get_sleep_type_name(999), "unknown")

    @patch.dict(os.environ, {"INFLUXDB_ADMIN_TOKEN": "test_token"})
    @patch("fitlog.influx_writer.InfluxDBClient")
    def test_write_invalid_data(self, mock_client):
        """不正なデータ書き込みのテスト"""
        writer = InfluxWriter()

        invalid_data = [
            {"measurement": "steps"},  # value と timestamp が不足
            {"value": 1000},  # measurement と timestamp が不足
            {"timestamp": 1234567890},  # measurement と value が不足
        ]

        result = writer.write_health_data(invalid_data)

        self.assertEqual(result, 0)


if __name__ == "__main__":
    unittest.main()
