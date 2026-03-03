from transformers.pipelines import pipeline
from typing import Any, TypedDict


# Percentage of the total response that is Action, Result, Situation, Task
class percentages(TypedDict):
    """Distribution of STAR components"""
    action: float
    result: float
    situation: float
    task: float


# StarScore type
class StarScore(TypedDict):
    """STAR results for response"""
    fufilledStar: bool
    percentages: percentages
    classifications: list[list[str]]


def predict_star_scores(*args) -> dict[str, Any]:
    """
    Predict STAR scores for feedback
    """
    """
    Predicts star scores
    Parameters:
    data (dict: {"text": (The sentence to be predicted: str)}): The data to be predicted on
    Returns:
    str: The predicted star label
    """
    #should only need to be set once
    classifier = pipeline("text-classification", model="dnttestmee/starclass_bert")  # type: ignore
    def predict(sentence) -> str:
        """
        Predicts the star label
        Parameters:
        sentence (str): The single sentence to be predicted
        Returns:
        str: The predicted star label
        """
        labels = {
            "LABEL_0": "Action",
            "LABEL_1": "Result",
            "LABEL_2": "Situation",
            "LABEL_3": "Task",
        }
        model_output: Any = classifier(sentence)
        # Single Label output.
        result: str = labels[str(model_output[0]["label"])]
        return result

    # Get the text from the data.
    data = args[0]["text"]
    # Split the text into sentences.
    sentences: list = data.split(".")
    # Contains sentence and label sentence type. 
    classifications = []
    # Classify each sentence
    for sentence in sentences:
        if sentence == "":
            continue
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
    action: float = round(action / total * 100, 2)
    result: float = round(result / total * 100, 2)
    situation: float = round(situation / total * 100, 2)
    task: float = round(task / total * 100, 2)
    if action > 0 and result > 0 and situation > 0 and task > 0:
        # If hits all categories, return True
        return {
            "fufilledStar": True,
            "percentages": {
                "action": action,
                "result": result,
                "situation": situation,
                "task": task,
            },
            "classifications": classifications,
        }
    return {
        "fufilledStar": False,
        "percentages": {
            "action": action,
            "result": result,
            "situation": situation,
            "task": task,
        },
        "classifications": classifications,
    }


def percentageFeedback(percentages):
    """
    Set Pre-determined feedback based on the final STAR value produced
    """
    feedback = []
    if (
        percentages["action"] > 0
        and percentages["result"] > 0
        and percentages["situation"] > 0
        and percentages["task"] > 0
    ):
        feedback.append(
            "You have fulfilled all of the parts the STAR method. Well done!"
        )

    if percentages["action"] < 60:
        feedback.append(
            "You need to work on the Action category. Percentage of your Response that is Action: "
            + str(percentages["action"])
            + " The Action category is the most important part of the STAR method. Try to focus on what you did and how you did it. The expected percentage for the Action category is 60% of your total response."
        )
    if percentages["result"] < 15:
        feedback.append(
            "You need to work on the Result category. Percentage of your Response that is Result:"
            + str(percentages["result"])
            + "The Result category is the most important part of the STAR method. Try to focus on outcomes related to your task or action. The expected percentage for the Result category is 10% of your total response."
        )
    if percentages["situation"] < 15:
        feedback.append(
            "You need to work on the Situation category. Percentage of your Response that is Situation:"
            + str(percentages["situation"])
            + "Try to focus on the context of the Situation and the circumstances that lead you to the task. The expected percentage for the Result category is 10% of your total response."
        )
    if percentages["task"] < 10:
        feedback.append(
            "You need to work on the Task category. Percentage of your Response that is Task:"
            + str(percentages["task"])
            + "The Task category is the most important part of the STAR method. Try to focus on the task itself. The expected percentage for the Task category is 10% of your total response."
        )

    return feedback
