import spacy
from textblob import TextBlob
import re

class FeedbackGenerator:
    def __init__(self):
        """첨삭 생성기 초기화"""
        # 영어 언어 모델 로드
        self.nlp = spacy.load("en_core_web_sm")
        
    def generate_detailed_feedback(self, student_answer, model_answer, problem_type):
        """학생 답안에 대한 상세 피드백 생성"""
        feedback = {
            "overall_score": 0,
            "grammar_feedback": [],
            "content_feedback": [],
            "vocabulary_feedback": [],
            "suggestions": [],
            "positive_points": [],
            "korean_summary": ""
        }
        
        # 문제 유형별 분석
        if problem_type == "영작문":
            feedback = self._analyze_writing(student_answer, model_answer, feedback)
        elif problem_type == "문법":
            feedback = self._analyze_grammar(student_answer, model_answer, feedback)
        elif problem_type == "어휘":
            feedback = self._analyze_vocabulary(student_answer, model_answer, feedback)
        else:
            feedback = self._analyze_general(student_answer, model_answer, feedback)
            
        # 종합 점수 계산
        feedback["overall_score"] = self._calculate_overall_score(feedback)
        
        # 한글 요약 생성
        feedback["korean_summary"] = self._generate_korean_summary(feedback)
        
        return feedback

    def _check_basic_grammar(self, doc):
        """기본 문법 규칙 검사"""
        errors = []
        
        # 주어-동사 일치 검사
        for sent in doc.sents:
            subject = None
            main_verb = None
            
            for token in sent:
                # 주어 찾기
                if token.dep_ == "nsubj":
                    subject = token
                # 주동사 찾기
                if token.pos_ == "VERB" and token.dep_ in ["ROOT", "VERB"]:
                    main_verb = token
                    
            if subject and main_verb:
                # 3인칭 단수 현재형 검사
                if subject.text.lower() in ["he", "she", "it"] and \
                   main_verb.tag_ == "VBP":  # base form instead of 3rd person
                    errors.append({
                        "error": "주어-동사 불일치",
                        "context": f"{subject.text} {main_verb.text}",
                        "suggestion": f"{subject.text} {main_verb.text}s",
                        "explanation": "3인칭 단수 주어는 동사에 -s를 붙여야 합니다."
                    })
        
        # 관사 사용 검사
        for token in doc:
            if token.pos_ == "NOUN" and token.dep_ not in ["compound"]:
                has_det = any(child.pos_ == "DET" for child in token.children)
                if not has_det and not token.tag_ == "NNS":  # 복수형이 아닌 경우
                    errors.append({
                        "error": "관사 누락",
                        "context": token.text,
                        "suggestion": f"a/the {token.text}",
                        "explanation": "가산명사 단수형 앞에는 관사가 필요합니다."
                    })
        
        return errors

    def _analyze_writing(self, student_answer, model_answer, feedback):
        """영작문 분석"""
        student_doc = self.nlp(student_answer)
        
        # 기본 문법 오류 검사
        grammar_errors = self._check_basic_grammar(student_doc)
        feedback["grammar_feedback"].extend(grammar_errors)
        
        # 문장 구조 분석
        feedback["content_feedback"].extend(self._analyze_sentence_structure(student_doc))
        
        # 어휘 다양성 분석
        feedback["vocabulary_feedback"].extend(self._analyze_vocabulary_diversity(student_doc))
        
        # 긍정적인 부분 찾기
        feedback["positive_points"].extend(self._find_positive_points(student_answer, model_answer))
        
        return feedback

    def _analyze_grammar(self, student_answer, model_answer, feedback):
        """문법 문제 분석"""
        student_doc = self.nlp(student_answer)
        
        # 기본 문법 오류 검사
        grammar_errors = self._check_basic_grammar(student_doc)
        feedback["grammar_feedback"].extend(grammar_errors)
        
        # 특정 문법 요소 분석
        feedback["grammar_feedback"].extend(self._analyze_specific_grammar(student_doc))
        
        return feedback

    def _analyze_vocabulary(self, student_answer, model_answer, feedback):
        """어휘 문제 분석"""
        student_words = set(word.lower() for word in student_answer.split())
        model_words = set(word.lower() for word in model_answer.split())
        
        # 누락된 주요 어휘 확인
        missing_words = model_words - student_words
        if missing_words:
            feedback["vocabulary_feedback"].append({
                "point": "누락된 주요 어휘",
                "details": list(missing_words),
                "suggestion": "다음 단어들을 포함하면 좋았을 것 같습니다."
            })
        
        # 부적절한 단어 사용 확인
        student_doc = self.nlp(student_answer)
        feedback["vocabulary_feedback"].extend(self._analyze_word_choice(student_doc))
        
        return feedback

    def _analyze_general(self, student_answer, model_answer, feedback):
        """일반적인 문제 분석"""
        # 기본적인 비교 분석
        student_blob = TextBlob(student_answer)
        model_blob = TextBlob(model_answer)
        
        # 감정 분석
        if student_blob.sentiment.polarity != model_blob.sentiment.polarity:
            feedback["content_feedback"].append({
                "point": "글의 어조",
                "details": "답안의 전반적인 어조가 모범 답안과 다릅니다.",
                "suggestion": "글의 목적에 맞는 어조를 사용하세요."
            })
        
        # 문장 길이 분석
        if len(student_blob.sentences) != len(model_blob.sentences):
            feedback["content_feedback"].append({
                "point": "문장 구성",
                "details": f"모범 답안은 {len(model_blob.sentences)}개의 문장으로 구성되어 있습니다.",
                "suggestion": "적절한 문장 분할을 고려해보세요."
            })
        
        return feedback

    def _analyze_sentence_structure(self, doc):
        """문장 구조 분석"""
        feedback = []
        
        # 문장 길이 분석
        sent_lengths = [len(sent) for sent in doc.sents]
        avg_length = sum(sent_lengths) / len(sent_lengths) if sent_lengths else 0
        
        if avg_length > 30:
            feedback.append({
                "point": "문장 길이",
                "details": "문장이 너무 길어 이해하기 어려울 수 있습니다.",
                "suggestion": "긴 문장을 여러 개의 짧은 문장으로 나누어 보세요."
            })
        
        # 구조 다양성 분석
        sentence_starts = []
        for sent in doc.sents:
            first_token = next(sent.iter_tokens())
            sentence_starts.append(first_token.pos_)
        
        if len(set(sentence_starts)) < 2:
            feedback.append({
                "point": "문장 구조 다양성",
                "details": "비슷한 구조의 문장이 반복됩니다.",
                "suggestion": "다양한 문장 구조를 사용하여 글의 흐름을 개선해보세요."
            })
        
        return feedback

    def _analyze_vocabulary_diversity(self, doc):
        """어휘 다양성 분석"""
        feedback = []
        
        # 어휘 다양성 계산
        words = [token.text.lower() for token in doc if token.is_alpha]
        unique_words = set(words)
        
        if len(words) > 0:
            diversity_ratio = len(unique_words) / len(words)
            
            if diversity_ratio < 0.4:  # 40% 미만의 어휘 다양성
                feedback.append({
                    "point": "어휘 다양성",
                    "details": "같은 단어가 자주 반복되고 있습니다.",
                    "suggestion": "유의어를 활용하여 더 다양한 표현을 시도해보세요."
                })
        
        # 고급 어휘 사용 분석
        advanced_words = 0
        for token in doc:
            if token.is_alpha and len(token.text) > 8:  # 8글자 이상의 단어를 고급 어휘로 간주
                advanced_words += 1
        
        if len(words) > 0 and advanced_words / len(words) < 0.1:  # 고급 어휘 비율 10% 미만
            feedback.append({
                "point": "어휘 수준",
                "details": "기초적인 어휘가 주로 사용되었습니다.",
                "suggestion": "상황에 맞는 더 정확하고 세련된 어휘를 사용해보세요."
            })
        
        return feedback

    def _analyze_word_choice(self, doc):
        """단어 선택 분석"""
        feedback = []
        
        # 자주 사용되는 기초 동사 목록
        basic_verbs = {"be", "have", "do", "make", "get", "go", "take", "come", "see", "know"}
        
        # 기초 동사 사용 빈도 분석
        basic_verb_count = 0
        total_verbs = 0
        
        for token in doc:
            if token.pos_ == "VERB":
                total_verbs += 1
                if token.lemma_.lower() in basic_verbs:
                    basic_verb_count += 1
        
        if total_verbs > 0 and basic_verb_count / total_verbs > 0.6:  # 기초 동사 비율 60% 초과
            feedback.append({
                "point": "동사 선택",
                "details": "기초적인 동사가 많이 사용되었습니다.",
                "suggestion": "더 구체적이고 상황에 맞는 동사를 사용해보세요."
            })
        
        # 부적절한 단어 조합 분석
        for i in range(len(doc) - 1):
            token = doc[i]
            next_token = doc[i + 1]
            
            if token.pos_ == "ADJ" and next_token.pos_ == "ADJ":
                feedback.append({
                    "point": "형용사 중복",
                    "details": f"'{token.text} {next_token.text}'와 같이 형용사가 연속으로 사용되었습니다.",
                    "suggestion": "더 자연스러운 표현으로 수정해보세요."
                })
        
        return feedback

    def _analyze_specific_grammar(self, doc):
        """특정 문법 요소 분석"""
        feedback = []
        
        # 시제 일관성 검사
        tenses = []
        for token in doc:
            if token.pos_ == "VERB" and token.morph.get("Tense"):
                tenses.extend(token.morph.get("Tense"))
        
        if len(set(tenses)) > 1:
            feedback.append({
                "point": "시제 일관성",
                "details": "문장 내에서 시제가 일관되지 않습니다.",
                "suggestion": "글의 문맥에 맞는 일관된 시제를 사용하세요."
            })
        
        return feedback

    def _find_positive_points(self, student_answer, model_answer):
        """긍정적인 부분 찾기"""
        positive_points = []
        
        # 문장 길이의 적절성 평가
        student_sents = [sent.string.strip() for sent in self.nlp(student_answer).sents]
        if all(10 <= len(sent.split()) <= 25 for sent in student_sents):
            positive_points.append("문장의 길이가 적절하여 읽기 쉽습니다.")
        
        # 고급 어휘 사용 평가
        student_doc = self.nlp(student_answer)
        advanced_words = [token.text for token in student_doc if token.is_alpha and len(token.text) > 8]
        if advanced_words:
            positive_points.append(f"'{', '.join(advanced_words[:3])}' 등의 고급 어휘를 적절히 사용했습니다.")
        
        # 문법적 정확성 평가
        grammar_errors = self._check_basic_grammar(self.nlp(student_answer))
        if len(grammar_errors) <= 2:
            positive_points.append("전반적으로 문법이 정확합니다.")
        
        # 모범 답안과의 유사도 평가
        student_doc = self.nlp(student_answer)
        model_doc = self.nlp(model_answer)
        similarity = student_doc.similarity(model_doc)
        
        if similarity > 0.8:
            positive_points.append("모범 답안의 핵심 내용을 잘 반영했습니다.")
        elif similarity > 0.6:
            positive_points.append("주요 내용을 적절히 포함하고 있습니다.")
        
        return positive_points

    def _calculate_overall_score(self, feedback):
        """종합 점수 계산"""
        # 기본 점수 시작 (100점 만점)
        score = 100
        
        # 문법 오류당 감점
        grammar_deduction = len(feedback["grammar_feedback"]) * 5
        score -= min(grammar_deduction, 30)  # 최대 30점 감점
        
        # 어휘 사용 문제당 감점
        vocabulary_deduction = len(feedback["vocabulary_feedback"]) * 5
        score -= min(vocabulary_deduction, 20)  # 최대 20점 감점
        
        # 내용 문제당 감점
        content_deduction = len(feedback["content_feedback"]) * 5
        score -= min(content_deduction, 30)  # 최대 30점 감점
        
        # 긍정적인 부분당 가점
        positive_points = len(feedback["positive_points"]) * 2
        score += min(positive_points, 10)  # 최대 10점 가점
        
        return max(0, min(score, 100))  # 0-100 범위 유지

    def _generate_korean_summary(self, feedback):
        """한글 요약 생성"""
        summary = []
        
        # 전체 평가 요약
        summary.append(f"📊 종합 점수: {feedback['overall_score']}점")
        
        # 긍정적인 부분
        if feedback["positive_points"]:
            summary.append("\n💪 잘한 점:")
            for point in feedback["positive_points"]:
                summary.append(f"- {point}")
        
        # 문법 피드백
        if feedback["grammar_feedback"]:
            summary.append("\n📝 문법 관련 의견:")
            for error in feedback["grammar_feedback"][:3]:  # 주요 오류 3개만
                summary.append(f"- {error['error']}")
                if 'suggestion' in error:
                    summary.append(f"  → 제안: {error['suggestion']}")
        
        # 어휘 피드백
        if feedback["vocabulary_feedback"]:
            summary.append("\n📚 어휘 관련 의견:")
            for feedback_item in feedback["vocabulary_feedback"]:
                summary.append(f"- {feedback_item['point']}")
                if 'suggestion' in feedback_item:
                    summary.append(f"  → 제안: {feedback_item['suggestion']}")
        
        # 내용 피드백
        if feedback["content_feedback"]:
            summary.append("\n💡 내용 관련 의견:")
            for feedback_item in feedback["content_feedback"]:
                summary.append(f"- {feedback_item['point']}")
                if 'suggestion' in feedback_item:
                    summary.append(f"  → 제안: {feedback_item['suggestion']}")
        
        # 전체적인 제안
        if feedback["suggestions"]:
            summary.append("\n✨ 향상을 위한 제안:")
            for suggestion in feedback["suggestions"]:
                summary.append(f"- {suggestion}")
        
        return "\n".join(summary) 