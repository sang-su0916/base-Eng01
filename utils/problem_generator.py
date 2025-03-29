import pandas as pd
from typing import List, Dict

class ProblemGenerator:
    @staticmethod
    def generate_basic_problems() -> List[Dict]:
        """기본 문제 20개를 생성합니다."""
        problems = [
            # 초급 문법 문제
            {
                "title": "Basic Grammar 1",
                "type": "문법",
                "difficulty": "초급",
                "time_limit": 15,
                "content": "Choose the correct form of the verb: He ___ (play) basketball every weekend.",
                "keywords": "play plays played playing",
                "model_answer": "He plays basketball every weekend."
            },
            {
                "title": "Basic Grammar 2",
                "type": "문법",
                "difficulty": "초급",
                "time_limit": 15,
                "content": "Fill in the blank with the correct article (a, an, the): I saw ___ elephant at the zoo.",
                "keywords": "a an the",
                "model_answer": "I saw an elephant at the zoo."
            },
            # 초급 어휘 문제
            {
                "title": "Basic Vocabulary 1",
                "type": "어휘",
                "difficulty": "초급",
                "time_limit": 10,
                "content": "What is the opposite of 'happy'?",
                "keywords": "sad unhappy opposite emotion",
                "model_answer": "The opposite of 'happy' is 'sad'."
            },
            {
                "title": "Basic Vocabulary 2",
                "type": "어휘",
                "difficulty": "초급",
                "time_limit": 10,
                "content": "Complete the word: App__ (fruit)",
                "keywords": "apple fruit food",
                "model_answer": "Apple"
            },
            # 초급 독해 문제
            {
                "title": "Basic Reading 1",
                "type": "독해",
                "difficulty": "초급",
                "time_limit": 20,
                "content": """Read the passage:
                Tom has a pet dog. His dog is black and white.
                The dog likes to play with a ball.
                
                Question: What color is Tom's dog?""",
                "keywords": "black white dog pet color",
                "model_answer": "Tom's dog is black and white."
            },
            # 중급 문법 문제
            {
                "title": "Intermediate Grammar 1",
                "type": "문법",
                "difficulty": "중급",
                "time_limit": 20,
                "content": "Complete the sentence using the present perfect tense: She ___ (live) in Paris for five years.",
                "keywords": "has have lived living",
                "model_answer": "She has lived in Paris for five years."
            },
            # 중급 어휘 문제
            {
                "title": "Intermediate Vocabulary 1",
                "type": "어휘",
                "difficulty": "중급",
                "time_limit": 15,
                "content": "Choose the correct word: The weather was ___ (terrible/terrific) yesterday. We had sunshine all day!",
                "keywords": "terrible terrific weather positive",
                "model_answer": "The weather was terrific yesterday."
            },
            # 중급 독해 문제
            {
                "title": "Intermediate Reading 1",
                "type": "독해",
                "difficulty": "중급",
                "time_limit": 25,
                "content": """Read the passage:
                Sarah loves to cook. Every weekend, she tries a new recipe.
                Last weekend, she made a chocolate cake for her family.
                Everyone said it was delicious.
                
                Question: What did Sarah make last weekend?""",
                "keywords": "cook recipe chocolate cake weekend",
                "model_answer": "Sarah made a chocolate cake last weekend."
            },
            # 고급 문법 문제
            {
                "title": "Advanced Grammar 1",
                "type": "문법",
                "difficulty": "고급",
                "time_limit": 25,
                "content": "Rewrite the sentence in reported speech: He said, 'I am going to the party tonight.'",
                "keywords": "reported speech indirect tense change",
                "model_answer": "He said that he was going to the party that night."
            },
            # 고급 어휘 문제
            {
                "title": "Advanced Vocabulary 1",
                "type": "어휘",
                "difficulty": "고급",
                "time_limit": 20,
                "content": "Choose the most appropriate word: The scientist's ___ (hypothesis/theory/guess) was supported by years of research.",
                "keywords": "hypothesis theory guess research scientific",
                "model_answer": "The scientist's hypothesis was supported by years of research."
            }
        ]
        
        return problems

    @staticmethod
    def save_to_csv(problems: List[Dict], filepath: str) -> None:
        """문제를 CSV 파일로 저장합니다."""
        df = pd.DataFrame(problems)
        df.to_csv(filepath, index=False)

    @staticmethod
    def save_to_json(problems: List[Dict], filepath: str) -> None:
        """문제를 JSON 파일로 저장합니다."""
        df = pd.DataFrame(problems)
        df.to_json(filepath, orient='records') 