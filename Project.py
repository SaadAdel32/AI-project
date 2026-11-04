
import pandas as pd
import numpy as np

# 1. Load dataset
df = pd.read_excel("Dataset_Brief_1.xlsx", sheet_name="Dataset_50000")

print("Original:", df.shape)

# 2. Remove duplicates
df.drop_duplicates(inplace=True)
df.drop_duplicates(subset="Incident_ID", keep="first", inplace=True)

print("After duplicates:", df.shape)

# 3. Replace empty values
df.replace(r"^\s*$", np.nan, regex=True, inplace=True)

# 4. Fix numeric columns
columns = ["Severity", "Humidity", "Latitude", "Longitude",
           "Speed_Limit", "Vehicle_Count", "Temperature",
           "Wind_Speed", "Average_Speed", "Traffic_Density",
           "Emergency_Response_Time"]

for col in columns:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# 5. Fix dates
df["Start_Time"] = pd.to_datetime(df["Start_Time"], errors="coerce")
df["End_Time"] = pd.to_datetime(df["End_Time"], errors="coerce")

# 6. Fix inconsistent text
for col in df.select_dtypes(include="object").columns:
    df[col] = df[col].str.strip()

# 7. Replace invalid values with NaN
df.loc[~df["Severity"].between(1, 4), "Severity"] = np.nan
df.loc[~df["Humidity"].between(0, 100), "Humidity"] = np.nan
df.loc[~df["Latitude"].between(-90, 90), "Latitude"] = np.nan
df.loc[~df["Longitude"].between(-180, 180), "Longitude"] = np.nan
df.loc[df["Speed_Limit"] < 0, "Speed_Limit"] = np.nan
df.loc[df["Vehicle_Count"] < 0, "Vehicle_Count"] = np.nan

# 8. Fill missing numeric values
for col in df.select_dtypes(include=np.number).columns:
    if df[col].notna().any():
        df[col] = df[col].fillna(df[col].median())

# 9. Fill missing text values
for col in df.select_dtypes(include="object").columns:
    if not df[col].mode().empty:
        df[col] = df[col].fillna(df[col].mode()[0])

# 10. Handle outliers using IQR
outlier_cols = ["Temperature", "Wind_Speed",
                "Average_Speed", "Traffic_Density",
                "Emergency_Response_Time"]

for col in outlier_cols:
    Q1 = df[col].quantile(0.25)
    Q3 = df[col].quantile(0.75)
    IQR = Q3 - Q1

    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR

    df[col] = df[col].clip(lower, upper)

# 11. Check invalid date order without deleting rows
invalid_dates = (
    df["Start_Time"].notna() &
    df["End_Time"].notna() &
    (df["End_Time"] < df["Start_Time"])
)

print("Invalid date order:", invalid_dates.sum())

# Mark incorrect end dates as missing
df.loc[invalid_dates, "End_Time"] = pd.NaT

# 12. Check results
print("Final shape:", df.shape)
print("Missing values:", df.isnull().sum().sum())
print("Duplicates:", df.duplicated().sum())
print("Missing dates:")
print(df[["Start_Time", "End_Time"]].isnull().sum())

# 13. Save cleaned dataset
df.to_csv("Cleaned_Dataset.csv", index=False)

print("Cleaning completed!")
