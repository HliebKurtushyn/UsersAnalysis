import pandas as pd

df = pd.read_csv('data/2019-Nov.csv', nrows=1000000)

# print(df.columns.tolist())
# print(df.info())
# print(df.describe())

print("--Analysis--")

print("\nEvent types")
event_types = df.event_type.value_counts()
print(event_types)

print("\nEvent percentage")
event_percentage = df.event_type.value_counts(normalize=True) * 100
print(event_percentage)

print("\nEvent summary")
event_summary = pd.DataFrame([event_types, event_percentage])
print(event_summary)

print("\nNull analysis")
print(df.isnull().sum() / len(df) * 100)

duplicates = df.duplicated().sum()
print(f"\nDuplicates before removal: {duplicates}")
if duplicates > 0:
    df = df.drop_duplicates().reset_index(drop=True)
duplicates = df.duplicated().sum()
print(f"Duplicates after removal: {duplicates}")

print("\nNull cleaning..")
df.brand = df.brand.fillna('Unknown')
df.category_code = df.category_code.fillna('Unknown')
print("Finished")

print("\nNull analysis after cleaning")
print(df.isnull().sum() / len(df) * 100)