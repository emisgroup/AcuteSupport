import os
import re

def apply_trend_classification(df, trends_path):
    """
    Reads trends from trends_path and applies keyword-based classification
    to the 'trend' column of the given dataframe.
    Also returns trend_keywords and trends for downstream processing.
    """
    trends = []
    if os.path.exists(trends_path):
        with open(trends_path, 'r', encoding='utf-8') as f:
            for line in f:
                t = line.strip()
                if t:
                    trends.append(t)
                    
    trend_keywords = []
    if trends:
        for t in trends:
            # create list of tokens
            tokens = re.split('[/,]', t)
            tokens = [tt.strip() for tt in tokens if tt.strip()]
            trend_keywords.append((t, tokens))

        def classify_trend(row):
            text = ' '.join([str(row.get('short_description','') or ''), str(row.get('description','') or '')]).lower()
            for trend_name, tokens in trend_keywords:
                for tok in tokens:
                    tok = tok.lower()
                    if tok and tok in text:
                        return trend_name
            return 'Other'

        df['trend'] = df.apply(classify_trend, axis=1)
    else:
        df['trend'] = 'Not classified'
        
    return df, trends, trend_keywords
