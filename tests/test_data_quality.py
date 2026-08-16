import os
import pandas as pd
import pytest

DATA_DIR = "data"

# 1. Test presence of core directories and metadata
def test_directory_structure():
    expected_paths = [
        "data/cleaned/01_student_performance/student_math.csv",
        "data/cleaned/02_student_dropout/student_dropout.csv",
        "data/cleaned/03_oulad/studentInfo.parquet",
        "data/ml_ready/dropout_prediction/student_dropout_ml_ready.csv",
        "metadata/data_dictionary.xlsx",
        "metadata/ml_schema.xlsx",
    ]
    for path in expected_paths:
        assert os.path.exists(path), f"Missing expected dataset file: {path}"

# 2. Test Student Dropout & Performance CSVs
def test_csv_datasets():
    csv_files = [
        "data/cleaned/01_student_performance/student_math.csv",
        "data/cleaned/01_student_performance/student_portuguese.csv",
        "data/cleaned/02_student_dropout/student_dropout.csv",
    ]
    for path in csv_files:
        df = pd.read_csv(path)
        assert not df.empty, f"File {path} is empty."
        assert len(df.columns) > 1, f"File {path} has no valid columns."

# 3. Test OULAD Parquet Files
def test_parquet_datasets():
    parquet_path = "data/cleaned/03_oulad/studentInfo.parquet"
    df = pd.read_parquet(parquet_path)
    assert not df.empty, f"Parquet file {parquet_path} contains no rows."

# 4. Test ML-Ready Training Data
def test_ml_ready_dataset():
    ml_data_path = "data/ml_ready/dropout_prediction/student_dropout_ml_ready.csv"
    df = pd.read_csv(ml_data_path)
    assert not df.empty, "ML-ready dropout dataset is empty."
    # Ensure no completely empty feature columns
    assert df.isnull().all().sum() == 0, "Found 100% missing value columns in ML-ready data."