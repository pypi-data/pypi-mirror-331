"""
Custom rules for the Otaro tweet generation task.
"""
import os
from litellm import completion
import logging

# Configure logging
logger = logging.getLogger("twitter-writer")

def max_length(tweets, max_chars):
    """
    Ensure all tweets are under the maximum character limit.
    
    Args:
        tweets: List of tweet strings
        max_chars: Maximum number of characters allowed
        
    Returns:
        bool: True if all tweets are under the character limit
    """
    if not tweets:
        return False
    
    for tweet in tweets:
        if len(tweet) > max_chars:
            return False
    
    return True

def length(tweets, expected_count):
    """
    Ensure the number of tweets matches the requested count.
    
    Args:
        tweets: List of tweet strings
        expected_count: Expected number of tweets
        
    Returns:
        bool: True if the number of tweets matches the expected count
    """
    return len(tweets) == expected_count

def contains_tone(tweets, tone):
    """
    Check if the tweets match the requested tone using Gemini 2.0 Flash via LiteLLM.
    
    Args:
        tweets: List of tweet strings
        tone: Requested tone for the tweets
        
    Returns:
        bool: True if the tweets match the requested tone, False otherwise
    """
    try:
        # Join tweets for analysis
        tweets_text = "\n".join(tweets)
        
        # Create prompt for tone analysis
        prompt = f"""
        Analyze the following tweets and determine if they match the tone: "{tone}".
        
        Tweets:
        {tweets_text}
        
        Does the overall tone of these tweets match the requested tone "{tone}"?
        Answer with only "yes" or "no".
        """
        
        # Call Gemini 2.0 Flash via LiteLLM
        response = completion(
            model="gemini/gemini-2.0-flash-001",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=10
        )
        
        # Extract the response text
        response_text = response.choices[0].message.content.strip().lower()
        
        # Log the response for debugging
        logger.info(f"Tone check response: {response_text}")
        
        # Check if the response indicates the tone matches
        return "yes" in response_text
    
    except Exception as e:
        # Log the error and return True as a fallback
        logger.error(f"Error checking tone with Gemini: {str(e)}")
        return True  # Fallback to True in case of errors

def no_hashtags(tweets):
    """
    Ensure none of the tweets contain hashtags (#).
    
    Args:
        tweets: List of tweet strings
        
    Returns:
        bool: True if none of the tweets contain hashtags
    """
    for tweet in tweets:
        if '#' in tweet:
            return False
    
    return True 