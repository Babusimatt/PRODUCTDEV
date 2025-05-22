import plotly.express as px
import pandas as pd

def get_summary_stats(df):
    return df.describe(include='all').to_string()

def sales_by(df, category):
    return px.histogram(df, x=category, color='event_type', barmode='group',
                        title=f"Sales Metrics by {category.capitalize()}")

def top_marketing_strategies(df):
    summary = df.groupby(['location', 'marketing_source']).size().reset_index(name='count')
    return px.bar(summary, x='location', y='count', color='marketing_source',
                  title='Top Marketing Strategies by Region')

def detect_anomalies(df):
    df_grouped = df.groupby('day').size().reset_index(name='events')
    threshold = df_grouped['events'].mean() + 2 * df_grouped['events'].std()
    df_grouped['anomaly'] = df_grouped['events'] > threshold
    return px.line(df_grouped, x='day', y='events', markers=True,
                   title='Anomalies in Activity', color='anomaly')
