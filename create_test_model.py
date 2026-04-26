"""
Create a simple test model for demonstration.
This model intentionally has some bias for testing purposes.
"""
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib

# Load data
df = pd.read_csv('test_hiring_data.csv')

# Prepare features and target
X = df[['age', 'experience', 'education_years', 'skills_score']]
y = df['hired']

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# Train model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Save model
joblib.dump(model, 'test_hiring_model.pkl')

print("✅ Model created and saved as 'test_hiring_model.pkl'")
print(f"Training accuracy: {model.score(X_train, y_train):.2%}")
print(f"Test accuracy: {model.score(X_test, y_test):.2%}")
