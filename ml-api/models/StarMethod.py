import pickle
import torch
import json
from helpers.text_processor import clean_text
from models.models import STAR_MODEL, STAR_TOKENIZER, LABEL_MAPPING

    
def predict_star_scores(data):
    """
    Predicts star scores
    """
    # Encode labels into numerical values
    model = STAR_MODEL
    tokenizer = STAR_TOKENIZER
    # Load the label mapping
    label_mapping = LABEL_MAPPING 
    # Function to predict the label of a given sentence
    def predict(sentence):
        inputs = tokenizer(sentence, return_tensors="pt", truncation=True, padding=True, max_length=128)
        outputs = model(**inputs)
        logits = outputs.logits
        predicted_class_id = torch.argmax(logits, dim=1).item()
        predicted_label = label_mapping[str(predicted_class_id)]
        return predicted_label 

    # split the data into sentences.  
    data = data["text"]  
    sentences = data.split(".")
    classifications = []
    for sentence in sentences:
        classifications.append([sentence, (predict(sentence))])
    # Figure out what percentage of the total text is Action, Result, Situation, Task
    action = 0
    result = 0
    situation = 0
    task = 0
    for i in classifications:
        if i[1] == "Action":
            action += 1
        elif i[1] == "Result":
            result += 1
        elif i[1] == "Situation":
            situation += 1
        elif i[1] == "Task":
            task += 1
    total = action + result + situation + task
    # Round to 2 decimal places
    action = round(action / total*100, 2)
    result = round(result / total*100, 2)
    situation = round(situation / total*100, 2)
    task = round(task / total*100, 2) 
    if action > 0 and result > 0 and situation > 0 and task > 0:
        # If hits all categories, return True 
        return { "fufilledStar": True, "percentages": {"action": action, "result": result, "situation": situation, "task": task}, "classifications": classifications}
    return { "fufilledStar": False, "percentages": {"action": action, "result": result, "situation": situation, "task": task}, "classifications": classifications} 

def percentageFeedback(percentages):
    """
    Returns feedback based on the percentages
    """ 
    feedback = []
    if percentages["action"] > 0 and percentages["result"] > 0 and percentages["situation"] > 0 and percentages["task"] > 0:
        feedback.append("You have fulfilled all of the parts the STAR method. Well done!")
        
    if percentages["action"] < 60:
        feedback.append("You need to work on the Action category. Percentage of your Response that is Action: " + str(percentages["action"]) + " The Action category is the most important part of the STAR method. Try to focus on what you did and how you did it. The expected percentage for the Action category is 60% of your total response.")
    if percentages["result"] < 15:
        feedback.append("You need to work on the Result category. Percentage of your Response that is Result:" + str(percentages["result"]) + "The Result category is the most important part of the STAR method. Try to focus on outcomes related to your task or action. The expected percentage for the Result category is 10% of your total response.")
    if percentages["situation"] < 15:
        feedback.append("You need to work on the Situation category. Percentage of your Response that is Situation:" + str(percentages["situation"]) + "Try to focus on the context of the Situation and the circumstances that lead you to the task. The expected percentage for the Result category is 10% of your total response." )
    if percentages["task"] < 10:
        feedback.append("You need to work on the Task category. Percentage of your Response that is Task:" + str(percentages["task"]) + "The Task category is the most important part of the STAR method. Try to focus on the task itself. The expected percentage for the Task category is 10% of your total response.")


    return feedback

