import boto3
import os
import sys
from datetime import datetime

def synthesize_speech(text_file, output_file, bucket_name, s3_key):
    """
    Synthesize speech from text file and upload to S3
    
    Args:
        text_file: Path to input text file
        output_file: Local output filename
        bucket_name: S3 bucket name
        s3_key: S3 object key (path)
    """
    # Read text content
    try:
        with open(text_file, 'r', encoding='utf-8') as f:
            text = f.read()
    except FileNotFoundError:
        print(f"Error: {text_file} not found")
        sys.exit(1)
    
    # Initialize Polly client
    polly_client = boto3.client('polly', region_name='us-east-1')
    
    # Synthesize speech
    print(f"Synthesizing speech from {text_file}...")
    try:
        response = polly_client.synthesize_speech(
            Text=text,
            OutputFormat='mp3',
            VoiceId='Joanna',
            Engine='neural'
        )
    except Exception as e:
        print(f"Error synthesizing speech: {e}")
        sys.exit(1)
    
    # Save audio to file
    print(f"Saving audio to {output_file}...")
    with open(output_file, 'wb') as f:
        f.write(response['AudioStream'].read())
    
    # Upload to S3
    print(f"Uploading to S3: s3://{bucket_name}/{s3_key}")
    s3_client = boto3.client('s3', region_name='us-east-1')
    try:
        s3_client.upload_file(
            output_file,
            bucket_name,
            s3_key,
            ExtraArgs={'ContentType': 'audio/mpeg'}
        )
        print(f"✓ Successfully uploaded to S3")
        print(f"  URL: https://{bucket_name}.s3.amazonaws.com/{s3_key}")
    except Exception as e:
        print(f"Error uploading to S3: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Get configuration from environment variables
    bucket_name = os.environ.get('S3_BUCKET_NAME')
    environment = os.environ.get('ENVIRONMENT', 'beta')
    
    if not bucket_name:
        print("Error: S3_BUCKET_NAME environment variable not set")
        sys.exit(1)
    
    # Configuration
     if environment == 'beta':
        text_file = 'speech-beta.txt'
    else:
        text_file = 'speech.txt'
    
    output_file = 'output.mp3'
    s3_key = f'polly-audio/{environment}.mp3'
    
    print(f"=== Polly Text-to-Speech Synthesis ===")
    print(f"Environment: {environment}")
    print(f"Input: {text_file}")
    print(f"Output: {output_file}")
    print(f"S3 Destination: s3://{bucket_name}/{s3_key}")
    print()
    
    synthesize_speech(text_file, output_file, bucket_name, s3_key)
    
    print("\n✓ Process completed successfully!")
