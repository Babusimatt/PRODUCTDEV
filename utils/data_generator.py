import pandas as pd
import random
from faker import Faker
import numpy as np

fake = Faker()

def generate_synthetic_data(n=1000):
    data = []
    event_types = ['job_placed', 'job_requested', 'demo_request', 'assistant_request']
    marketing_sources = ['Google Ads', 'LinkedIn', 'Newsletter', 'Webinar']
    locations = [
        'UK', 'USA', 'Germany', 'India', 'South Africa', 'France', 'Spain', 'Canada',
        'Mexico', 'China', 'Japan', 'Nigeria', 'Kenya', 'Australia', 'New Zealand',
        'Brazil', 'Italy', 'Russia'
    ]

    for _ in range(n):
        timestamp = fake.date_time_between(start_date='-3y', end_date='now')
        ip = fake.ipv4()
        location = random.choice(locations)
        age = random.randint(18, 65)
        job_type = random.choice(['AI assistant', 'Prototype', 'Analytics Tool'])
        event_type = random.choice(event_types)
        marketing = random.choice(marketing_sources)

        data.append({
            'timestamp': timestamp,
            'ip': ip,
            'location': location,
            'age': age,
            'job_type': job_type,
            'event_type': event_type,
            'marketing_source': marketing
        })

    df = pd.DataFrame(data)
    df['hour'] = df['timestamp'].dt.hour
    df['day'] = df['timestamp'].dt.date
    return df

