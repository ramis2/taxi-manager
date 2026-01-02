# Create a clean virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install from requirements.txt
pip install -r requirements.txt

# Test if app runs
streamlit run app.py

