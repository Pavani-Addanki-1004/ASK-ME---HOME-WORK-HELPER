import pandas as pd
import json
from nlp_workshop import clean_sent

def load_hotpotqa_data():
    """Loads HotpotQA dataset into a DataFrame"""
    file_paths = [
        r'C:\Users\ajeev\Downloads\hotpotqa_dataset\hotpot_dev_distractor_v1.json',
        r'C:\Users\ajeev\Downloads\hotpotqa_dataset\hotpot_dev_fullwiki_v1.json',
        r'C:\Users\ajeev\Downloads\hotpotqa_dataset\hotpot_test_fullwiki_v1.json',
        r'C:\Users\ajeev\Downloads\hotpotqa_dataset\hotpot_train_v1.1.json'
    ]
    data = []
    for file in file_paths:
        with open(file, 'r', encoding='utf-8') as f:
            data.extend(json.load(f))
    return pd.DataFrame(data)

data_df = load_hotpotqa_data()

def create_output(question):
    print(f"Received question: {question}")  # Debugging
    question = clean_sent(question)
    
    results = data_df[data_df['question'].str.contains(question, case=False, na=False)]
    print(f"Matching results: {results}")  # Debugging
    
    if not results.empty:
        return results.iloc[0]['answer']
    
    return "No relevant answer found."
