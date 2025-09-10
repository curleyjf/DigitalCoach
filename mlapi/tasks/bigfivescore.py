from enum import Enum


class TraitLevel(Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class BigFiveScores:
    def __init__(self, o: float, c: float, e: float, a: float, n: float):
        self.o = o
        self.c = c
        self.e = e
        self.a = a
        self.n = n

    def determine_level(self, score: float) -> TraitLevel:
        if score < -3:
            return TraitLevel.LOW
        elif score > 3:
            return TraitLevel.HIGH
        else:
            return TraitLevel.MEDIUM

    FEEDBACK = {
        "openness": {
            TraitLevel.LOW: "With an Openness score less than -3, you are more likely to stick to your routines, avoid change and follow a traditional thought process.",
            TraitLevel.MEDIUM: "With an Openness score between -3 and 3, you are somewhat open to new experiences and creative, but you still enjoy some structure and consistency.",
            TraitLevel.HIGH: "With an Openness score greater than 3, you likely enjoy trying new things, are creative and imaginative and can easily think about problems in different ways.",
        },
        "conscientiousness": {
            TraitLevel.LOW: "With a Conscientiousness score less than -3, you are likely less organized and more willing to finish tasks at the last minute.",
            TraitLevel.MEDIUM: "With a Conscientiousness score between -3 and 3, you accept some level of order, but also like doing some things at your own pace.",
            TraitLevel.HIGH: "With a Conscientiousness score greater than 3, you are always prepared, keep things in order and are very goal driven.",
        },
        "extraversion": {
            TraitLevel.LOW: "With an Extraversion score less than -3, you may struggle to socialize and prefer keeping to yourself.",
            TraitLevel.MEDIUM: "With an Extraversion score between -3 and 3, you enjoy your personal time but also like the occasional exciting activity or large gathering.",
            TraitLevel.HIGH: "With an Extraversion score greater than 3, you live for excitement and like to be around others. You recharge with others rather than without them.",
        },
        "agreeableness": {
            TraitLevel.LOW: "With an Agreeableness score less than -3, you likely focus more on yourself and care less about how others feel about you.",
            TraitLevel.MEDIUM: "With an Agreeableness score between -3 and 3, you are willing to help others and care about them, but still prioritize yourself.",
            TraitLevel.HIGH: "With an Agreeableness score greater than 3, you care about others, are always ready to help them and see the best in them.",
        },
        "neuroticism": {
            TraitLevel.LOW: "With a Neuroticism score less than -3, you are able to remain calm even in high stress situations. You also remain optimistic and do not worry so much.",
            TraitLevel.MEDIUM: "With a Neuroticism score between -3 and 3, you have some confidence in yourself and can stay calm in somewhat stressful situations, but still carry self doubts.",
            TraitLevel.HIGH: "With a Neuroticism score greater than 3, you may be very insecure and get stressed out easily, and you tend to blame yourself when things go wrong.",
        },
    }


def big_five_feedback(scores: dict[str, float]) -> list[str]:
    """
    Gets the feedback for the big five scores
    """
    big_five = BigFiveScores(
        scores["o"], scores["c"], scores["e"], scores["a"], scores["n"]
    )
    user_feedback = []
    for trait, attr in zip(
        [
            "openness",
            "conscientiousness",
            "extraversion",
            "agreeableness",
            "neuroticism",
        ],
        ["o", "c", "e", "a", "n"],
    ):
        trait_level = big_five.determine_level(getattr(big_five, attr))
        user_feedback.append(BigFiveScores.FEEDBACK[trait][trait_level])
    return user_feedback
