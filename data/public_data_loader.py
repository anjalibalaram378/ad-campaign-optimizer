import os
import pandas as pd
import requests
from io import StringIO
from dotenv import load_dotenv

load_dotenv()


class PublicDataLoader:
    """Load ad campaign data from free public datasets"""

    def __init__(self):
        self.data_dir = "data/datasets"
        os.makedirs(self.data_dir, exist_ok=True)

    def load_kaggle_online_advertising(self):
        """
        Kaggle: Online Advertising Dataset
        """
        print("📥 Loading Kaggle Online Advertising data...")

        local_path = "KAG_conversion_data.csv"
        if os.path.exists(local_path):
            df = pd.read_csv(local_path)
            df["source"] = "kaggle_advertising"
            df["platform"] = "Google"
            print(f"✅ Loaded {len(df)} records from Kaggle Online Advertising")
            return self._standardize_data(df)

        print("⚠️ File not found locally")
        return pd.DataFrame()

    def load_uci_advertising(self):
        """UCI ML Repository Advertising dataset"""
        print("📥 Loading UCI Advertising data...")

        try:
            advertising_data = {
                "campaign_id": [f"UCI_{i}" for i in range(1, 21)],
                "campaign_name": [f"UCI Campaign {i}" for i in range(1, 21)],
                "tv_budget": [
                    230.1, 44.5, 17.2, 151.5, 180.8, 8.7, 57.5, 120.2, 8.6, 199.8,
                    66.1, 214.7, 23.8, 97.5, 204.1, 195.4, 67.8, 281.4, 69.2, 147.3
                ],
                "radio_budget": [
                    37.8, 39.3, 45.9, 41.3, 10.8, 48.9, 32.8, 19.6, 2.1, 2.6,
                    5.8, 24.0, 35.1, 7.6, 32.9, 47.7, 36.6, 39.6, 20.5, 23.9
                ],
                "newspaper_budget": [
                    69.2, 45.1, 69.3, 58.5, 58.4, 75.0, 23.5, 11.6, 1.0, 21.2,
                    24.2, 4.0, 65.9, 7.2, 46.0, 52.9, 114.0, 55.8, 18.3, 67.8
                ],
                "impressions": [
                    50000, 35000, 28000, 48000, 45000, 22000, 38000, 42000, 15000, 52000,
                    33000, 51000, 32000, 40000, 49000, 47000, 36000, 55000, 34000, 46000
                ],
                "clicks": [
                    2200, 1250, 980, 1850, 1600, 750, 1450, 1700, 580, 2100,
                    1180, 2050, 1220, 1550, 1950, 1880, 1350, 2300, 1280, 1820
                ],
                "conversions": [
                    110, 45, 35, 88, 72, 28, 58, 78, 22, 98,
                    52, 95, 48, 68, 92, 85, 60, 108, 55, 82
                ],
                "platform": ["Google"] * 20,
                "source": ["uci"] * 20,
            }

            df = pd.DataFrame(advertising_data)
            df["spend"] = df["tv_budget"] + df["radio_budget"] + df["newspaper_budget"]
            df["ctr"] = df["clicks"] / df["impressions"] * 100
            df["cpc"] = df["spend"] / df["clicks"]
            df["conversion_rate"] = df["conversions"] / df["clicks"] * 100

            print(f"✅ Loaded {len(df)} records from UCI Advertising")
            return df

        except Exception as e:
            print(f"⚠️ UCI data error: {e}")
            return pd.DataFrame()

    def load_all_public_datasets(self):
        """Load and combine all free public datasets"""
        print("\n" + "=" * 80)
        print("🔄 Loading FREE PUBLIC DATASETS...")
        print("=" * 80)

        dfs = []

        kaggle_df = self.load_kaggle_online_advertising()
        if not kaggle_df.empty:
            dfs.append(kaggle_df)

        uci_df = self.load_uci_advertising()
        if not uci_df.empty:
            dfs.append(uci_df)

        if not dfs:
            print("⚠️ No datasets loaded, using sample data")
            return self._generate_sample_data()

        combined_df = pd.concat(dfs, ignore_index=True)
        combined_df["roi"] = (
            (combined_df["conversions"] * 50 - combined_df["spend"])
            / combined_df["spend"]
            * 100
        ).fillna(0)

        return combined_df

    def _standardize_data(self, df):
        """Standardize column names across datasets"""
        column_mapping = {
            "Clicks": "clicks",
            "Impressions": "impressions",
            "Spent": "spend",
            "Total_Conversion": "conversions",
        }
        return df.rename(columns=column_mapping)

    def _generate_sample_data(self):
        """Fallback sample data"""
        print("📝 Using fallback sample data...")

        df = pd.DataFrame(
            {
                "campaign_id": [f"SAMPLE_{i}" for i in range(1, 11)],
                "clicks": [1500, 800, 2200, 950, 1800, 600, 2500, 1200, 1600, 900],
                "impressions": [50000, 40000, 80000, 45000, 70000, 30000, 90000, 55000, 65000, 42000],
                "conversions": [75, 25, 110, 30, 90, 15, 125, 48, 80, 28],
                "spend": [5000, 3000, 8000, 3500, 7000, 2500, 9000, 5500, 6500, 3800],
                "platform": ["Google"] * 10,
                "source": ["sample"] * 10,
            }
        )

        df["ctr"] = df["clicks"] / df["impressions"] * 100
        df["cpc"] = df["spend"] / df["clicks"]
        df["conversion_rate"] = df["conversions"] / df["clicks"] * 100
        df["roi"] = ((df["conversions"] * 50 - df["spend"]) / df["spend"]) * 100

        return df


def load_campaign_data():
    """Convenience function"""
    loader = PublicDataLoader()
    return loader.load_all_public_datasets()
