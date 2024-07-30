import json
import requests
import pandas as pd
import boto3
from datetime import datetime
from io import StringIO

# Define the S3 bucket name
BUCKET_NAME = "eco-data-cache"

def fetch_api_data(url, headers) -> dict:
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise ValueError(f"Error: {response.status_code}, unable to fetch data from the API.")
    return response.json()

def convert_to_dataframe(data) -> pd.DataFrame:
    # Create a DataFrame from the 'standing' key in the JSON data
    try:
        df = pd.DataFrame(data['standing'])
        # Expand 'country' & 'medals' into separate columns
        df = pd.concat([df.drop(['country', 'medals'], axis=1), df['country'].apply(pd.Series), df['medals'].apply(pd.Series)], axis=1).drop(columns=['urn'])
    except Exception as e:
        print(f"Error: {e}")
        df = pd.DataFrame()
    return df

def save_to_s3(dataframe, bucket_name, file_path):
    csv_buffer = StringIO()
    dataframe.to_csv(csv_buffer, index=False)
    s3_client = boto3.client('s3')
    s3_client.put_object(
        Bucket=bucket_name, 
        Key=file_path, 
        Body=csv_buffer.getvalue(), 
        ACL='public-read'  # Set the ACL to make the object publicly accessible
    )

def load_csv_from_s3(bucket_name, file_key):
    s3_client = boto3.client('s3')
    csv_obj = s3_client.get_object(Bucket=bucket_name, Key=file_key)
    body = csv_obj['Body']
    csv_string = body.read().decode('utf-8')
    df = pd.read_csv(StringIO(csv_string))
    return df
    
def lambda_handler(event, context):
    # Define the API URL and headers
    url = 'https://web-cdn.api.bbci.co.uk/wc-poll-data/container/sport-olympics-medals?tournament=paris-2024'
    headers = {
        'accept': 'application/json',
        'accept-language': 'en-GB,en;q=0.7',
        # 'if-none-match': '"e0086ea4e830e3bcc82cc414da1b34931a3c4466"',    # add this header to get 304 response, likely corresponds to our web session
        'origin': 'https://www.bbc.co.uk',
        'priority': 'u=1, i',
        'referer': 'https://www.bbc.co.uk/',
        'sec-ch-ua': '"Brave";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'sec-gpc': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
    }

    # 1. Fetch API data
    data = fetch_api_data(url, headers)

    # 2. Convert data to DataFrame
    df = convert_to_dataframe(data)
    
    # # 3. [OPTIONAL] Load the indicators dataset from S3 - e.g. could be population & GDP data by country
    # indicators_file_key = "olympics/live_results/indicators.csv"
    # df19 = load_csv_from_s3(BUCKET_NAME, indicators_file_key)
    # # Merge the datasets
    # merged_df = df.merge(df19.drop(columns=['name']), left_index=True, right_on='GSScode', how='left')
    
    # Get the current timestamp and format it
    timestamp = datetime.now().strftime("%Y%m%d-%H%M")
    
    # Define the file path in S3 for the merged dataset
    merged_file_path = "olympics/live_results/medals.csv"
    
    # Save the merged DataFrame to S3
    save_to_s3(df, BUCKET_NAME, merged_file_path)
    
    # Log the file upload success
    print(f"File {merged_file_path} successfully uploaded to S3 bucket {BUCKET_NAME}.")
    
    return {
        'statusCode': 200,
        'body': json.dumps(f"File {merged_file_path} successfully uploaded to S3 bucket {BUCKET_NAME}.")
    }

# Define the main function to test locally
if __name__ == "__main__":
    lambda_handler({}, {})
