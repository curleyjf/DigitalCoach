import json

def generate_feedback(data):
    feedback = []

    
    sentiments = data.get('sentiment_analysis', [])
    highlights = data.get('highlights', {}).get('results', [])
    
    # Use Timestamps to assess confidence
    for sentiment_data in sentiments:
        sentiment = sentiment_data['sentiment']
        text = sentiment_data['text']
        start_time = sentiment_data['start'] / 1000  # Convert ms to seconds
        end_time = sentiment_data['end'] / 1000  # Convert ms to seconds
        confidence = sentiment_data['confidence']

        time_range = f"{start_time:.2f}s - {end_time:.2f}s"
        if confidence < 0.6:
            # Confidence Low feedback
            feedback.append(
                f"In the segment from {time_range}, the sentiment confidence was low ({confidence:.2f}). "
                f"Consider clarifying your message: '{text}'."
            )
        else:
            # Default Feedback
            feedback.append(
                f"In the segment from {time_range}, your sentiment was detected as '{sentiment}'. "
                f"The text '{text}' had a confidence of {confidence:.2f}."
            )

    # Track repeated phrases, won't include pauses or umms.  
    if highlights:
        for highlight in highlights:
            count = highlight.get('count', 0)
            text = highlight.get('text', '')
            timestamps = highlight.get('timestamps', [])
            # Feedback on repeated phrases (might be too specific)
            if count > 1:
                time_ranges = ", ".join(
                    f"{ts['start']/1000:.2f}s - {ts['end']/1000:.2f}s" for ts in timestamps
                )
                feedback.append(
                    f"The phrase '{text}' was repeated {count} times at these times: {time_ranges}. "
                    f"Possibly consider varying your language to keep the conversation engaging."
                )

    # IAB Results feedback, making sure the user is on topic (could match with the question topics)
    iab_results = data.get('iab_results', {}).get('results', [])
    if iab_results:
        relevant_topics = iab_results[0].get('labels', [])
        relevant_topics = sorted(relevant_topics, key=lambda x: -x['relevance'])
        most_relevant = relevant_topics[0] if relevant_topics else None
        # Most relevant topic.
        if most_relevant:
            label = most_relevant['label']
            relevance = most_relevant['relevance']
            feedback.append(
                f"The most relevant topic detected was '{label}' with a relevance score of {relevance:.2f}. "
                f"Consider this area if it aligns with your intended message."
            )
     
    

    return "\n".join(feedback)

# Input data this would be the result from the API: response = /results/jobID; response.sentiment_analysis
data = {
    'sentiment_analysis': [
        {'sentiment': 'NEUTRAL', 'text': 'Testing.', 'start': 1600, 'end': 2008, 'confidence': 0.7255797, 'speaker': None},
        {'sentiment': 'NEUTRAL', 'text': 'Once again.', 'start': 2008, 'end': 2536, 'confidence': 0.5508492, 'speaker': None},
        {'sentiment': 'NEUTRAL', 'text': 'Testing.', 'start': 2577, 'end': 2905, 'confidence': 0.7255797, 'speaker': None}
    ],
    'highlights': {
        'status': 'success',
        'results': [
            {'count': 2, 'rank': 0.47, 'text': 'Testing', 'timestamps': [{'start': 1600, 'end': 2008}, {'start': 2577, 'end': 2905}]}
        ]
    },
    'iab_results': {
        'status': 'success',
        'results': [
            {'text': 'Testing. Once again. Testing.',
             'labels': [
                 {'relevance': 0.89795536, 'label': 'MedicalHealth>MedicalTests'},
                 {'relevance': 0.5599882, 'label': 'Education>EducationalAssessment'}
             ],
             'timestamp': {'start': 1600, 'end': 2905},
             'sentences_idx_end': 2,
             'sentences_idx_start': 0}
        ]
    },
    'clip_length_seconds': 4.06
}
# Generate feedback
feedback = generate_feedback(data)
print(feedback)
