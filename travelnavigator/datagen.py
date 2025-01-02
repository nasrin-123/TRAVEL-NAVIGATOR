import requests
import pandas as pd
import time
import random
import json

# Base API parameters
API_BASE_URL = "https://integrate.api.nvidia.com/v1"
API_KEY = "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"  # Replace with your valid API key

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Load the original dataset from a CSV file
input_csv_path = "merged_dataset.csv"  # Replace with your input CSV file path
df = pd.read_csv(input_csv_path)

# Ensure dataset contains the required columns
if "QUESTIONS" not in df.columns or "ANSWERS" not in df.columns:
    raise ValueError("The dataset must contain 'QUESTIONS' and 'ANSWERS' columns.")

# Initialize an empty list to store the synthetic dataset
synthetic_data = []

# Number of variations per original question
variations_per_entry = 2  # Generate multiple variations per question
max_retries = 2  # Number of retries for failed requests

def make_request_with_retries(payload, max_retries=3):
    """
    Make an API request with retry logic and handle streamed responses.
    """
    delay = 1  # Initial delay in seconds
    for attempt in range(max_retries):
        try:
            response = requests.post(f"{API_BASE_URL}/chat/completions", json=payload, headers=headers, stream=True)
            if response.status_code == 200:
                # Process streamed response
                content = ""
                for line in response.iter_lines(decode_unicode=True):
                    if line.startswith("data: "):  # Process only lines with "data: "
                        data = line[6:]  # Remove "data: "
                        if data == "[DONE]":
                            break  # End of stream
                        try:
                            chunk = json.loads(data)
                            delta_content = chunk.get("choices", [{}])[0].get("delta", {}).get("content", "")
                            content += delta_content
                        except json.JSONDecodeError:
                            print(f"Error decoding chunk: {data}")
                return content.strip()  # Return the concatenated content
            else:
                print(f"Attempt {attempt + 1} failed. Status Code: {response.status_code}. Response: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"Exception during request: {e}. Retrying after {delay} seconds...")
        time.sleep(delay)
        delay *= 2  # Exponential backoff
    return None  # Return None if all retries fail

# Generate synthetic data
for index, row in df.iterrows():
    question = row["QUESTIONS"]
    base_answer = row["ANSWERS"]

    # Track variations for the current question to ensure uniqueness
    current_variations = set()

    for _ in range(variations_per_entry):
        # Create the prompt with slight variation for diversity
        prompt_variation = random.choice([
            f"Rewrite the following answer in a unique way based on the question:\n"
            f"Question: {question}\n"
            f"Original Answer: {base_answer}\n",

            f"Provide a creative alternative answer to the following question:\n"
            f"Question: {question}\n"
            f"Original Answer: {base_answer}\n",

            f"Generate a different way to answer the question below:\n"
            f"Question: {question}\n"
            f"Original Answer: {base_answer}\n"
        ])

        payload = {
            "model": "nvidia/nemotron-4-340b-instruct",
            "messages": [{"role": "user", "content": prompt_variation}],
            "temperature": random.uniform(0.7, 1.0),  # Vary temperature for randomness
            "top_p": random.uniform(0.7, 0.9),  # Vary top_p for randomness
            "max_tokens": 512,
            "stream": True  # Enable streaming
        }

        # Make API request with retries
        synthetic_answer = make_request_with_retries(payload, max_retries=max_retries)

        if synthetic_answer:
            # Check for uniqueness
            if synthetic_answer not in current_variations:
                current_variations.add(synthetic_answer)
                synthetic_data.append({"question": question, "answer": synthetic_answer})
                print(f"Generated {len(synthetic_data)} synthetic entries.", end="\r")
            else:
                print(f"Duplicate response detected. Retrying for question: {question}")
        else:
            print(f"Failed to generate data for question: {question}. Skipping...")

        # Add a slight random delay to avoid rate limits
        time.sleep(random.uniform(0.1, 0.3))

# Save the synthetic dataset to a CSV file
output_csv_path = "synthetic_dataset.csv"
synthetic_df = pd.DataFrame(synthetic_data)

if not synthetic_df.empty:
    synthetic_df.to_csv(output_csv_path, index=False)
    print(f"\nSynthetic dataset saved to {output_csv_path}. Total entries: {len(synthetic_data)}")
else:
    print("\nNo synthetic data was generated. Please check the logs for errors.")
