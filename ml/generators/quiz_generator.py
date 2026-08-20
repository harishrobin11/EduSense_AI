"""AI Quiz Generator & Answer Evaluator for EduSense AI."""

import random
from typing import Dict, Any, List, Tuple


class AIQuizGenerator:
    """Engine generating multiple-choice quiz questions and evaluating student answers."""

    QUESTION_TEMPLATES = {
        "Python Programming": [
            {
                "question": "What is the primary purpose of {topic_name} in Python?",
                "options": [
                    "To structure data, enable code reusability, and manage program logic effectively.",
                    "To increase hardware GPU execution speed automatically.",
                    "To convert Python scripts into low-level assembly language.",
                    "To bypass memory management and garbage collection."
                ],
                "correct_index": 0,
                "explanation": "{topic_name} is used in Python to organize logic cleanly and write reusable code."
            },
            {
                "question": "Which keyword or syntax pattern is most commonly associated with {topic_name}?",
                "options": [
                    "Standard syntax structures defined in PEP 8 guidelines.",
                    "The 'goto' keyword used for jumping lines.",
                    "Exclusive C++ pointer dereferencing operator '*&'.",
                    "Direct hardware registers access directives."
                ],
                "correct_index": 0,
                "explanation": "Python follows PEP 8 standards for clean, readable syntax patterns."
            }
        ],
        "Mathematics for ML": [
            {
                "question": "In the context of {topic_name}, why is mathematical foundation crucial for Machine Learning?",
                "options": [
                    "It computes gradients, optimizes loss functions, and models data vector spaces accurately.",
                    "It replaces the need for data preprocessing and feature scaling.",
                    "It guarantees 100% accuracy on any uncleaned dataset.",
                    "It converts raw text data into HTML elements."
                ],
                "correct_index": 0,
                "explanation": "{topic_name} provides the mathematical framework for optimization, loss minimization, and linear transformation."
            },
            {
                "question": "What happens when you apply {topic_name} operations to high-dimensional feature matrices?",
                "options": [
                    "Vectors are transformed across vector spaces to compute magnitudes, directions, or rates of change.",
                    "Data points are randomly erased to save storage disk space.",
                    "The matrix is converted into a compressed audio file format.",
                    "The neural network model automatically stops learning."
                ],
                "correct_index": 0,
                "explanation": "Matrix transformations in {topic_name} measure vector projections, feature correlations, and derivative slopes."
            }
        ],
        "Machine Learning": [
            {
                "question": "When building a model using {topic_name}, what is the main objective during training?",
                "options": [
                    "To minimize empirical loss/cost function and generalize well to unseen test data.",
                    "To memorize 100% of training data without any validation split.",
                    "To maximize parameter variance until overfitting occurs.",
                    "To eliminate all mathematical weights and bias values."
                ],
                "correct_index": 0,
                "explanation": "{topic_name} aims to minimize loss and optimize decision boundaries for strong generalization."
            },
            {
                "question": "Which evaluation metric or diagnostic tool is most relevant when assessing {topic_name}?",
                "options": [
                    "Precision, Recall, ROC-AUC, or MSE depending on regression vs classification target.",
                    "Total count of lines in Python code script.",
                    "The execution clock speed of the web browser.",
                    "The file size of the synthetic raw dataset."
                ],
                "correct_index": 0,
                "explanation": "Evaluation metrics assess model error, false positive/negative trade-offs, and prediction accuracy."
            }
        ],
        "Deep Learning & NLP": [
            {
                "question": "How does {topic_name} improve feature representation compared to basic algorithms?",
                "options": [
                    "By leveraging deep layered abstractions, attention mechanisms, or contextual embeddings.",
                    "By replacing matrix multiplications with simple string concatenation.",
                    "By requiring zero training data or labels.",
                    "By turning all continuous values into binary booleans."
                ],
                "correct_index": 0,
                "explanation": "{topic_name} extracts multi-layer hierarchical abstractions and semantic contextual embeddings."
            }
        ]
    }

    def generate_quiz(
        self,
        topic_name: str,
        subject: str,
        difficulty: str = "medium",
        question_count: int = 3,
    ) -> List[Dict[str, Any]]:
        """Generate structured multiple-choice questions for a topic."""
        templates = self.QUESTION_TEMPLATES.get(subject, self.QUESTION_TEMPLATES["Machine Learning"])
        questions = []

        for q_idx in range(question_count):
            tmpl = templates[q_idx % len(templates)]
            q_text = tmpl["question"].format(topic_name=topic_name)
            opts = [o.format(topic_name=topic_name) for o in tmpl["options"]]

            # Shuffle options deterministically while tracking correct answer
            correct_opt = opts[tmpl["correct_index"]]
            random.seed(hash(f"{topic_name}_{difficulty}_{q_idx}"))
            shuffled_opts = opts.copy()
            random.shuffle(shuffled_opts)
            new_correct_idx = shuffled_opts.index(correct_opt)

            questions.append({
                "question_id": q_idx + 1,
                "question_text": f"[{difficulty.upper()}] {q_text}",
                "options": shuffled_opts,
                "correct_option_index": new_correct_idx,
                "explanation": tmpl["explanation"].format(topic_name=topic_name),
            })

        return questions

    def evaluate_quiz_answers(
        self,
        questions: List[Dict[str, Any]],
        user_answers: List[int],
    ) -> Tuple[float, int, List[Dict[str, Any]]]:
        """Evaluate student selected option indices and compute score percentage."""
        if not questions or len(user_answers) != len(questions):
            return 0.0, 0, []

        correct_count = 0
        breakdown = []

        for q, user_choice in zip(questions, user_answers):
            is_correct = user_choice == q["correct_option_index"]
            if is_correct:
                correct_count += 1

            breakdown.append({
                "question_id": q["question_id"],
                "question_text": q["question_text"],
                "user_selected_index": user_choice,
                "user_selected_option": q["options"][user_choice] if 0 <= user_choice < len(q["options"]) else "Invalid",
                "correct_option_index": q["correct_option_index"],
                "correct_option_text": q["options"][q["correct_option_index"]],
                "is_correct": is_correct,
                "explanation": q["explanation"],
            })

        score_pct = round((correct_count / len(questions)) * 100.0, 1)
        return score_pct, correct_count, breakdown


quiz_generator = AIQuizGenerator()
