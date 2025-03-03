from contextlib import nullcontext
from . import transcript_metrics as tm
import pandas as pd
from sklearn import preprocessing
import numpy as np
import os

def conv_analysis_processor(input, input_filename):
    print(f"Processing file: {input_filename}")

    # Split .txt file input into array of strings
    data = input.splitlines()
    data_time = input.splitlines()
    # Remove time data
    sep = '['
    for i in range(0, len(data)):             
        data[i] = data[i].split(sep, 1)[0]
    
    # Compute features
    semantic_A = tm.semantic(data, 'A')
    semantic_B = tm.semantic(data, 'B')
    semantic_C = tm.semantic(data, 'C')
    sent2_avg, sent_turns = tm.sent_model2(data)
    cqpt, tqpt, qr = tm.question(data)
    print(cqpt, tqpt, qr)

    features = {
        "Therapist_Words_in_Transcript/Conversation_Per_Turn": [tm.meanw_countT(data)],
        "Client_Words_in_Transcript/Conversation_Per_Turn": [tm.meanw_countC(data)],
        "Ratio_of_Therapist_Client_Words_in_Transcript/Conversation_Per_Turn": [tm.ratio_words(data)],

        "Client_Questions_in_Transcript/Conversation_Per_Turn": [cqpt],
        "Therapist_Questions_in_Transcript/Conversation_Per_Turn": [tqpt],
        "Ratio_of_Client_Question/Therapist_Questions_in_Transcript/Conversation_Per_Turn": [qr],

        "Client_Turns_in_Transcript/Conversation": [tm.C_turns(data)],
        "Therapist_Turns_in_Transcript/Conversation": [tm.T_turns(data)],
        "Ratio_of_Client_Therapist_Turns_in_Transcript/Conversation": [tm.ratio_turns(data)],
        
        "Average_Speaking_Time_of_Each_Speaker_in_Transcript/Conversation_Per_Turn": [tm.time_avg(data_time)],
        
        "STD_Therapist_Words_in_Transcript/Conversation": [tm.stdw_countT(data)],
        "Skew_Therapist_Words_in_Transcript/Conversation": [tm.skeww_countT(data)],
        "Kurt_Therapist_Words_in_Transcript/Conversation": [tm.kurtw_countT(data)],
        "STD_Client_Words_in_Transcript/Conversation": [tm.stdw_countC(data)],
        "Skew_Client_Words_in_Transcript/Conversation": [tm.skeww_countC(data)],
        "Kurt_Client_Words_in_Transcript/Conversation": [tm.kurtw_countC(data)],

        "MODEL_A_Sem_All_Avg": [semantic_A[0]],
        "MODEL_A_Sem_All_SD": [semantic_A[1]],
        "MODEL_A_Sem_All_Skew": [semantic_A[2]],
        "MODEL_A_Sem_All_Kurt": [semantic_A[3]],
        "MODEL_A_Sem_Adj_Avg": [semantic_A[4]],
        "MODEL_A_Sem_Adj_SD": [semantic_A[5]],
        "MODEL_A_Sem_Adj_Skew": [semantic_A[6]],
        "MODEL_A_Sem_Adj_Kurt": [semantic_A[7]],
        
        "MODEL_B_Sem_All_Avg": [semantic_B[0]],
        "MODEL_B_Sem_All_SD": [semantic_B[1]],
        "MODEL_B_Sem_All_Skew": [semantic_B[2]],
        "MODEL_B_Sem_All_Kurt": [semantic_B[3]],
        "MODEL_B_Sem_Adj_Avg": [semantic_B[4]],
        "MODEL_B_Sem_Adj_SD": [semantic_B[5]],
        "MODEL_B_Sem_Adj_Skew": [semantic_B[6]],
        "MODEL_B_Sem_Adj_Kurt": [semantic_B[7]],
        
        "MODEL_C_Sem_All_Avg": [semantic_C[0]],
        "MODEL_C_Sem_All_SD": [semantic_C[1]],
        "MODEL_C_Sem_All_Skew": [semantic_C[2]],
        "MODEL_C_Sem_All_Kurt": [semantic_C[3]],
        "MODEL_C_Sem_Adj_Avg": [semantic_C[4]],
        "MODEL_C_Sem_Adj_SD": [semantic_C[5]],
        "MODEL_C_Sem_Adj_Skew": [semantic_C[6]],
        "MODEL_C_Sem_Adj_Kurt": [semantic_C[7]],

        "Overall_Sentiment_of_Client": [sent2_avg],
        "Change_in_Client_Sentiment_in_Transcript/Conversation": [sent_turns]
    }

    # Save all feature data in a dataframe
    feature_df = pd.DataFrame(features)
    
    # Extract base filename without extension
    base_filename = input_filename.split('.')[0]
    
    # Create output directory if it doesn't exist
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "output_data")
    os.makedirs(output_dir, exist_ok=True)
    
    # Save to CSV in the output_data directory
    output_path = os.path.join(output_dir, f"{base_filename}_features.csv")
    feature_df.to_csv(output_path, index=False)
    print(f"Features saved to {output_path}")
    
    return feature_df