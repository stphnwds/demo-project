import pandas as pd

# 2. Creating a DataFrame
data = {
    "Name": ["John", "Anna", "Peter", "Linda"],
    "Age": [25, 36, 28, 32],
    "City": ["New York", "Paris", "Berlin", "London"],
}
df = pd.DataFrame(data)

df.head()
