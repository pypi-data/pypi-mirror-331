#Statistics Imports
import statistics
from scipy.stats import kurtosis, skew
#Semantic Similarity Imports
from sentence_transformers import SentenceTransformer, util
from promcse import PromCSE
#SentImports
from transformers import pipeline
#question Detection imports
from nltk.tokenize import word_tokenize, TweetTokenizer
from nltk import bigrams
#import regex
import re
import pandas as pd
import math

#==============================================================================
# SENTIMENT ANALYSIS FUNCTIONS
#==============================================================================

#Sent Features
def sent_model2(x):
  """
  Analyze sentiment of text segments and calculate average sentiment and turns.
  
  Args:
      x (list): List of text segments to analyze
      
  Returns:
      tuple: (average_sentiment, sentiment_turns)
          - average_sentiment: Rounded score (1=negative, 2=neutral, 3=positive)
          - sentiment_turns: Number of times sentiment changes between categories
  """
  # Initialize sentiment analysis model
  sentiment_pipeline = pipeline("sentiment-analysis", model = "cardiffnlp/twitter-roberta-base-sentiment-latest")
  data = x
  final_sentiment = sentiment_pipeline(data)
  
  # Initialize counters and scores
  final_score = [0, 0, 0]  # [negative, neutral, positive]
  sent_turn = 0  # sentiment turns counter
  total = 0
  prev = "hello"  # initialize previous sentiment
  
  print("\n" + "="*50)
  print("SENTIMENT ANALYSIS RESULTS")
  print("="*50)
  print(f"Initial scores: {final_score}")

  # Process each text segment
  for text in final_sentiment:
    print("\nAnalyzing segment:")
    print(f"  {text}")
    total = total + 1
    
    if "positive" in text["label"]:
      if prev != text["label"]:
        sent_turn = sent_turn + 1
        print(f"  Sentiment turn detected: {prev} → {text['label']}")
      final_score[2] = (1*text["score"]) + final_score[2]
    elif "negative" in text["label"]:
      if prev != text["label"]:
        sent_turn = sent_turn + 1
        print(f"  Sentiment turn detected: {prev} → {text['label']}")
      final_score[0] = final_score[0] + (1*text["score"])
    else:  # neutral
      if prev != text["label"]:
        sent_turn = sent_turn + 1
        print(f"  Sentiment turn detected: {prev} → {text['label']}")
      final_score[1] = final_score[1] + (1*text["score"])
    prev = text["label"]
    
  print("\nFinal sentiment scores:")
  print(f"  Negative: {final_score[0]:.2f}")
  print(f"  Neutral: {final_score[1]:.2f}")
  print(f"  Positive: {final_score[2]:.2f}")

  # Calculate weighted average (1=negative, 2=neutral, 3=positive)
  avg_score = ((1 * final_score[0]) + (2*final_score[1]) + (3*final_score[2]))/(total)
  avg_sentiment = round(avg_score)

  print(f"\nWeighted average sentiment: {avg_score:.2f}")
  print(f"Rounded sentiment score: {avg_sentiment}")
  print(f"Total sentiment turns: {sent_turn}")
  print("="*50)
  
  return avg_sentiment, sent_turn

#==============================================================================
# SEMANTIC SIMILARITY FUNCTIONS
#==============================================================================

#Semantic Features
def semantic(sentences, model_number):
  """
  Calculate semantic similarity metrics between sentences.
  
  Args:
      sentences (list): List of sentences to analyze
      model_number (str): Model selection ('A', 'B', or 'C')
      
  Returns:
      list: Eight statistical measures of semantic similarity
          [Average_All, SD_All, Skew_All, Kurt_All, 
           Average_Adj, SD_Adj, Skew_Adj, Kurt_Adj]
  """
  print("\n" + "="*50)
  print("SEMANTIC SIMILARITY ANALYSIS")
  print("="*50)
  print(f"Model selection: {model_number}")
  
  #Model A:
  if (model_number == 'A'):
    model = SentenceTransformer("Sakil/sentence_similarity_semantic_search")
    print("Using model: Sakil/sentence_similarity_semantic_search")
    
  #Model B:
  elif (model_number == 'B'):
    model = PromCSE("YuxinJiang/unsup-promcse-bert-base-uncased", "cls_before_pooler", 16)
    print("Using model: YuxinJiang/unsup-promcse-bert-base-uncased")

  #Model C
  elif (model_number == 'C'):
    model = SentenceTransformer('all-MiniLM-L6-v2')
    print("Using model: all-MiniLM-L6-v2")

  #Number of sentences
  n = len(sentences)
  print(f"Analyzing {n} sentences")

  #Encode all sentences
  print("Encoding sentences...")
  embeddings = model.encode(sentences)

  #Compute cosine similarity between all pairs
  print("Computing similarity matrix...")
  cos_sim = util.cos_sim(embeddings, embeddings)

  #Add all pairs to a list with their cosine similarity score
  all_sentence_combinations = []

  for i in range(len(cos_sim)-1):
    for j in range(i+1, len(cos_sim)):
      all_sentence_combinations.append([cos_sim[i][j], i, j])

  #Create an array of all unique sentence combinations
  unique_comparisons = []
  for i in range(0,(n)):
    for j in range(i+1, n):
      unique_comparisons.append(cos_sim[i][j].item())

  #Compute Statistical Measurements: All Sentences
  print("\nCalculating metrics for ALL sentence pairs:")
  Average_All = statistics.mean(unique_comparisons)
  SD_All = statistics.stdev(unique_comparisons)
  Skew_All = skew(unique_comparisons, axis = 0, bias = True)
  Kurt_All = kurtosis(unique_comparisons, axis = 0, fisher = True, bias = True)
  
  print(f"  Mean similarity: {Average_All:.4f}")
  print(f"  Standard deviation: {SD_All:.4f}")
  print(f"  Skewness: {Skew_All:.4f}")
  print(f"  Kurtosis: {Kurt_All:.4f}")

  #Create an array of all adjacent sentence combinations
  adj_comparisons = []
  print("\nExtracting ADJACENT sentence pairs:")
  for i in range(0,n-1):
    #uncomment to check which sentences are being compared
    #print("{} \t {} \t {:.4f}".format(sentences[i], sentences[i+1], cos_sim[i][i+1]))
    
    adj_comparisons.append(cos_sim[i][i+1].item())

  #Compute Statistical Measurements: Adjacent Sentences
  print("\nCalculating metrics for ADJACENT sentence pairs:")
  Average_Adj = statistics.mean(adj_comparisons)
  SD_Adj = statistics.stdev(adj_comparisons)
  Skew_Adj = skew(adj_comparisons, axis = 0, bias = True)
  Kurt_Adj = kurtosis(adj_comparisons, axis = 0, fisher = True, bias = True)
  
  print(f"  Mean similarity: {Average_Adj:.4f}")
  print(f"  Standard deviation: {SD_Adj:.4f}")
  print(f"  Skewness: {Skew_Adj:.4f}")
  print(f"  Kurtosis: {Kurt_Adj:.4f}")

  all_semantics = [Average_All, SD_All, Skew_All, Kurt_All, Average_Adj, SD_Adj, Skew_Adj, Kurt_Adj]
  print("="*50)
  
  return all_semantics

#==============================================================================
# STATISTICAL ANALYSIS - THERAPIST FUNCTIONS
#==============================================================================

#Gets mean words/turn Therapist
def meanw_countT(y):
  """
  Calculate mean words per turn for Therapist utterances.
  
  Args:
      y (list): List of utterances with speaker markers ('T:' or 'C:')
      
  Returns:
      float: Mean words per turn for Therapist
  """
  print("\n" + "="*50)
  print("THERAPIST WORD COUNT - MEAN")
  print("="*50)
  
  df = pd.DataFrame(columns = ['Word Count'])
  for sentence in y:
    if sentence[0] == 'T':
      df.loc[len(df)] = [len(sentence.split()) - 1]
  
  # Show data summary
  print("Word counts for Therapist utterances:")
  print(df.head().to_string())
  if len(df) > 5:
    print(f"... and {len(df)-5} more rows")
  
  mean_value = df['Word Count'].mean()
  print(f"\nTherapist Words/Turn: {mean_value:.2f}")
  print("="*50)
  
  return (mean_value)

#standard devation
def stdw_countT(y):
  """
  Calculate standard deviation of words per turn for Therapist utterances.
  
  Args:
      y (list): List of utterances with speaker markers ('T:' or 'C:')
      
  Returns:
      float or None: Standard deviation of words per turn for Therapist
  """
  print("\n" + "="*50)
  print("THERAPIST WORD COUNT - STANDARD DEVIATION")
  print("="*50)
  
  df = pd.DataFrame(columns = ['Word Count'])
  for sentence in y:
    if sentence[0] == 'T':
      df.loc[len(df)] = [len(sentence.split()) - 1]
  
  # Show data summary
  print("Word counts for Therapist utterances:")
  print(df.head().to_string())
  if len(df) > 5:
    print(f"... and {len(df)-5} more rows")
  
  std_value = df['Word Count'].std()
  if(math.isnan(std_value)):
    print("WARNING: Cannot calculate STD - insufficient data")
    print("="*50)
    return None
    
  print(f"STD Therapist Words/Turn: {std_value:.2f}")
  print("="*50)
  
  return (std_value)

#skewness
def skeww_countT(y):
  """
  Calculate skewness of words per turn for Therapist utterances.
  
  Args:
      y (list): List of utterances with speaker markers ('T:' or 'C:')
      
  Returns:
      float or None: Skewness of words per turn for Therapist
  """
  print("\n" + "="*50)
  print("THERAPIST WORD COUNT - SKEWNESS")
  print("="*50)
  
  df = pd.DataFrame(columns = ['Word Count'])
  for sentence in y:
    if sentence[0] == 'T':
      df.loc[len(df)] = [len(sentence.split()) - 1]
  
  # Show data summary
  print("Word counts for Therapist utterances:")
  print(df.head().to_string())
  if len(df) > 5:
    print(f"... and {len(df)-5} more rows")
  
  skew_value = df['Word Count'].skew()
  if(math.isnan(skew_value)):
    print("WARNING: Cannot calculate skewness - insufficient data")
    print("="*50)
    return None
    
  print(f"Skew Therapist Words/Turn: {skew_value:.2f}")
  print(f"Interpretation: {'Positive (right tail)' if skew_value > 0 else 'Negative (left tail)'}")
  print("="*50)
  
  return (skew_value)

#kurtosis
def kurtw_countT(y):
  """
  Calculate kurtosis of words per turn for Therapist utterances.
  
  Args:
      y (list): List of utterances with speaker markers ('T:' or 'C:')
      
  Returns:
      float or None: Kurtosis of words per turn for Therapist
  """
  print("\n" + "="*50)
  print("THERAPIST WORD COUNT - KURTOSIS")
  print("="*50)
  
  df = pd.DataFrame(columns = ['Word Count'])
  for sentence in y:
    if sentence[0] == 'T':
      df.loc[len(df)] = [len(sentence.split()) - 1]
  
  # Show data summary
  print("Word counts for Therapist utterances:")
  print(df.head().to_string())
  if len(df) > 5:
    print(f"... and {len(df)-5} more rows")
  
  kurt_value = df['Word Count'].kurt()
  if(math.isnan(kurt_value)):
    print("WARNING: Cannot calculate kurtosis - insufficient data")
    print("="*50)
    return None
    
  print(f"Kurt Therapist Words/Turn: {kurt_value:.2f}")
  print(f"Interpretation: {'Leptokurtic (heavy tails)' if kurt_value > 0 else 'Platykurtic (light tails)'}")
  print("="*50)
  
  return (kurt_value)

#==============================================================================
# STATISTICAL ANALYSIS - CLIENT FUNCTIONS
#==============================================================================

#Gets Average words/turn Client
def meanw_countC(y):
  """
  Calculate mean words per turn for Client utterances.
  
  Args:
      y (list): List of utterances with speaker markers ('T:' or 'C:')
      
  Returns:
      float: Mean words per turn for Client
  """
  print("\n" + "="*50)
  print("CLIENT WORD COUNT - MEAN")
  print("="*50)
  
  df = pd.DataFrame(columns = ['Word Count'])
  for sentence in y:
    if sentence[0] == 'C':
      df.loc[len(df)] = [len(sentence.split()) - 1]
  
  mean_value = df['Word Count'].mean()
  print(f"Number of Client utterances: {len(df)}")
  print(f"Client Words/Turn: {mean_value:.2f}")
  print("="*50)
  
  return mean_value

def stdw_countC(y):
  """
  Calculate standard deviation of words per turn for Client utterances.
  
  Args:
      y (list): List of utterances with speaker markers ('T:' or 'C:')
      
  Returns:
      float or None: Standard deviation of words per turn for Client
  """
  print("\n" + "="*50)
  print("CLIENT WORD COUNT - STANDARD DEVIATION")
  print("="*50)
  
  df = pd.DataFrame(columns = ['Word Count'])
  for sentence in y:
    if sentence[0] == 'C':
      df.loc[len(df)] = [len(sentence.split()) - 1]
  
  std_value = df['Word Count'].std()
  if(math.isnan(std_value)):
    print("WARNING: Cannot calculate STD - insufficient data")
    print("="*50)
    return None
    
  print(f"Number of Client utterances: {len(df)}")
  print(f"STD Client Words/Turn: {std_value:.2f}")
  print("="*50)
  
  return std_value

def skeww_countC(y):
  """
  Calculate skewness of words per turn for Client utterances.
  
  Args:
      y (list): List of utterances with speaker markers ('T:' or 'C:')
      
  Returns:
      float or None: Skewness of words per turn for Client
  """
  print("\n" + "="*50)
  print("CLIENT WORD COUNT - SKEWNESS")
  print("="*50)
  
  df = pd.DataFrame(columns = ['Word Count'])
  for sentence in y:
    if sentence[0] == 'C':
      df.loc[len(df)] = [len(sentence.split()) - 1]
  
  skew_value = df['Word Count'].skew()
  if(math.isnan(skew_value)):
    print("WARNING: Cannot calculate skewness - insufficient data")
    print("="*50)
    return None
    
  print(f"Number of Client utterances: {len(df)}")
  print(f"Skew Client Words/Turn: {skew_value:.2f}")
  print(f"Interpretation: {'Positive (right tail)' if skew_value > 0 else 'Negative (left tail)'}")
  print("="*50)
  
  return skew_value

def kurtw_countC(y):
  """
  Calculate kurtosis of words per turn for Client utterances.
  
  Args:
      y (list): List of utterances with speaker markers ('T:' or 'C:')
      
  Returns:
      float or None: Kurtosis of words per turn for Client
  """
  print("\n" + "="*50)
  print("CLIENT WORD COUNT - KURTOSIS")
  print("="*50)
  
  df = pd.DataFrame(columns = ['Word Count'])
  for sentence in y:
    if sentence[0] == 'C':
      df.loc[len(df)] = [len(sentence.split()) - 1]
  
  kurt_value = df['Word Count'].kurt()
  if(math.isnan(kurt_value)):
    print("WARNING: Cannot calculate kurtosis - insufficient data")
    print("="*50)
    return None
    
  print(f"Number of Client utterances: {len(df)}")
  print(f"Kurt Client Words/Turn: {kurt_value:.2f}")
  print(f"Interpretation: {'Leptokurtic (heavy tails)' if kurt_value > 0 else 'Platykurtic (light tails)'}")
  print("="*50)
  
  return kurt_value

#==============================================================================
# TURN-TAKING ANALYSIS FUNCTIONS
#==============================================================================

#Returns turns taken by therapist
def T_turns(y):
  """
  Count the number of turns taken by the Therapist.
  
  Args:
      y (list): List of utterances with speaker markers ('T:' or 'C:')
      
  Returns:
      int: Number of Therapist turns
  """
  print("\n" + "="*50)
  print("THERAPIST TURN COUNT")
  print("="*50)
  
  t_sentences = 0

  for sentence in y:
    if sentence[0] == 'T':
      t_sentences+=1

  print(f"Total Therapist turns: {t_sentences}")
  print("="*50)
  
  return t_sentences

#returns turns taken by client
def C_turns(y):
  """
  Count the number of turns taken by the Client.
  
  Args:
      y (list): List of utterances with speaker markers ('T:' or 'C:')
      
  Returns:
      int: Number of Client turns
  """
  print("\n" + "="*50)
  print("CLIENT TURN COUNT")
  print("="*50)
  
  c_sentences = 0

  for sentence in y:
    if sentence[0] == 'C':
      c_sentences+=1

  print(f"Total Client turns: {c_sentences}")
  print("="*50)
  
  return c_sentences

#returns ratio of turns T/C 
def ratio_turns(y):
  """
  Calculate the ratio of Therapist turns to Client turns.
  
  Args:
      y (list): List of utterances with speaker markers ('T:' or 'C:')
      
  Returns:
      float: Ratio of Therapist turns to Client turns
  """
  print("\n" + "="*50)
  print("TURN-TAKING RATIO ANALYSIS")
  print("="*50)
  
  c_sentences = 0
  t_sentences = 0

  for sentence in y:
    if sentence[0] == 'C':
      c_sentences+=1
    else:
      t_sentences+=1

  ratio = t_sentences/c_sentences if c_sentences > 0 else float('inf')
  
  print(f"Therapist turns: {t_sentences}")
  print(f"Client turns: {c_sentences}")
  print(f"Ratio (T/C): {ratio:.2f}")
  print(f"Interpretation: {'Therapist-dominated' if ratio > 1 else 'Client-dominated' if ratio < 1 else 'Equal participation'}")
  print("="*50)
  
  return ratio

#ratio of WPT_T  /  WPT_C
def ratio_words(y):
  """
  Calculate the ratio of Therapist words per turn to Client words per turn.
  
  Args:
      y (list): List of utterances with speaker markers ('T:' or 'C:')
      
  Returns:
      float: Ratio of Therapist words per turn to Client words per turn
  """
  print("\n" + "="*50)
  print("WORDS PER TURN RATIO ANALYSIS")
  print("="*50)
  
  t_mean = meanw_countT(y)
  c_mean = meanw_countC(y)
  
  ratio = t_mean/c_mean if c_mean > 0 else float('inf')
  
  print(f"Ratio of Therapist WPT to Client WPT: {ratio:.2f}")
  print(f"Interpretation: {'Therapist speaks more' if ratio > 1 else 'Client speaks more' if ratio < 1 else 'Equal verbosity'}")
  print("="*50)
  
  return ratio

#==============================================================================
# QUESTION DETECTION FUNCTIONS
#==============================================================================

#Question Features
#QUESTION word set and Auxillary verb word set combined
Set_A = ["what", "why", "when", "where", "who", "whom", "whose", "were",
                "which", "was", "does", "did", "can", "could", "will", "would", "should", "has",
                "have", "had", "may", "might", "shall", "should", "must", "be", "do", "have", "best", 
                "need", "shall", "better", "may", "should", "can", "might", "will",
                "could", "must", "would", "dare", "ought", "are", "to", "in", "of", "is", "i", "it", "?"]

def is_question(sentence):
    """
    Determine if a sentence is likely a question based on keywords.
    
    Args:
        sentence (str): The sentence to check
        
    Returns:
        bool: True if the sentence is likely a question, False otherwise
    """
    # Tokenize the input sentence
    tokens = word_tokenize(sentence.lower())

    # Check if any question words are present in the tokens
    if any(word in tokens for word in Set_A):
        return True
    else:
        return False
    
def question(x):
    """
    Analyze question usage patterns in a therapy transcript.
    
    Args:
        x (list): List of transcript lines with speaker indicators
        
    Returns:
        tuple: (client_questions_per_line, therapist_questions_per_line, client_therapist_question_ratio)
    """
    print("\n" + "="*50)
    print("QUESTION PATTERN ANALYSIS")
    print("="*50)
    
    transcript = x  # this is a list containing all lines of transcript
    length = len(transcript)
    print(f"Total transcript lines: {length}")
    
    c_cnt = 0  # Client question counter
    t_cnt = 0  # Therapist question counter
    
    print("\nAnalyzing question patterns...")
    for line in transcript:
        tknzr = TweetTokenizer()
        tokens = tknzr.tokenize(line)

        # Create word pairs (bigrams)
        word_pairs = list(bigrams(tokens))

        # Determine speaker
        inClient = None
        if len(word_pairs) >= 2:
            if(word_pairs[0][0] == 'C'):
                inClient = True
            elif(word_pairs[0][0] == 'T'):
                inClient = False

        # Look for question patterns in the bigrams
        for pair in word_pairs:
            if((pair[0] in Set_A) and (pair[1] in Set_A) or (pair[1] == "?")):
                if(inClient == True):
                    c_cnt+=1
                    
                    # Uncomment for detailed analysis:
                    # print(f"Client question detected: {line[:50]}...")
                elif(inClient == False):
                    t_cnt+=1
                    
                    # Uncomment for detailed analysis:
                    # print(f"Therapist question detected: {line[:50]}...")
                
                # Avoid incrementing multiple times if we hit a question mark in middle
                if(pair[1] == "?"):
                    break
    
    # Calculate metrics
    c_qperlines = c_cnt/length if length > 0 else 0
    t_qperlines = t_cnt/length if length > 0 else 0

    if t_cnt != 0 and c_cnt != 0:
        c_t_question_ratio = c_cnt/t_cnt
    else:
        c_t_question_ratio = None

    # Print results summary
    print("\nQUESTION ANALYSIS RESULTS:")
    print(f"Client questions: {c_cnt}")
    print(f"Therapist questions: {t_cnt}")
    print(f"Client questions per line: {c_qperlines:.4f}")
    print(f"Therapist questions per line: {t_qperlines:.4f}")
    
    if c_t_question_ratio is not None:
        print(f"Client/Therapist question ratio: {c_t_question_ratio:.2f}")
        print(f"Interpretation: {'Client asks more questions' if c_t_question_ratio > 1 else 'Therapist asks more questions'}")
    else:
        print("Client/Therapist question ratio: N/A (insufficient data)")
    
    print("="*50)
    return c_qperlines, t_qperlines, c_t_question_ratio

#==============================================================================
# TIME ANALYSIS FUNCTIONS
#==============================================================================

#Time Features
def time_avg(x):
    """
    Calculate the average duration time from transcript timestamps.
    
    Args:
        x (list): List of transcript lines with timestamps [00:XX]
        
    Returns:
        float: Average duration time in seconds
    """
    print("\n" + "="*50)
    print("TIME DURATION ANALYSIS")
    print("="*50)
    
    total_time = 0
    processed_lines = 0
    
    print("Processing timestamp data...")
    for sentence in x:
        try:
            # Extract duration time
            res = re.findall(r'\:.*?\]', sentence)
            if not res:
                continue
                
            temp = res[0]
            temp = temp.replace(':', '')
            temp = temp.replace(']', '')
            temp = temp.replace(' ', '')
            duration = int(temp)
            
            total_time += duration
            processed_lines += 1
            
            # Uncomment for detailed processing:
            # print(f"Line {processed_lines}: Duration = {duration}s")
            
        except (IndexError, ValueError) as e:
            print(f"Warning: Could not process time in line: {sentence[:30]}...")
    
    # Calculate average
    avg_duration = total_time/len(x) if len(x) > 0 else 0
    
    print(f"\nTotal processed duration: {total_time} seconds")
    print(f"Number of lines: {len(x)}")
    print(f"Average duration: {avg_duration:.2f} seconds")
    print("="*50)
    
    return avg_duration