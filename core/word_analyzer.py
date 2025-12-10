"""
Word Analyzer Module
Implements Zipf's Law for word frequency analysis and context-based word meaning extraction.
"""

import re
import math
from collections import Counter, defaultdict
from typing import Dict, List, Tuple, Optional, Set
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.tag import pos_tag
from nltk.chunk import ne_chunk

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

try:
    nltk.data.find('taggers/averaged_perceptron_tagger')
except LookupError:
    nltk.download('averaged_perceptron_tagger')


class ZipfsLawAnalyzer:
    """
    Analyzes word frequency distribution using Zipf's Law.
    Zipf's Law states that the frequency of a word is inversely proportional to its rank.
    """

    def __init__(self):
        """Initialize the Zipf's Law analyzer."""
        self.word_frequencies = Counter()
        self.ranked_words = []
        self.total_words = 0

    def analyze_text(self, text: str) -> Dict:
        """
        Analyze text using Zipf's Law principles.

        Args:
            text: Input text to analyze

        Returns:
            Dictionary containing frequency analysis and Zipf's Law metrics
        """
        # Tokenize and clean text
        tokens = self._tokenize_and_clean(text)
        self.total_words = len(tokens)
        
        # Count word frequencies
        self.word_frequencies = Counter(tokens)
        
        # Rank words by frequency
        self.ranked_words = self.word_frequencies.most_common()
        
        # Calculate Zipf's Law metrics
        zipf_metrics = self._calculate_zipf_metrics()
        
        return {
            'total_words': self.total_words,
            'unique_words': len(self.word_frequencies),
            'word_frequencies': dict(self.word_frequencies.most_common(50)),
            'zipf_metrics': zipf_metrics,
            'ranked_words': self.ranked_words[:50]
        }

    def _tokenize_and_clean(self, text: str) -> List[str]:
        """
        Tokenize and clean text for analysis.

        Args:
            text: Input text

        Returns:
            List of cleaned tokens
        """
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters but keep apostrophes for contractions
        text = re.sub(r"[^\w\s'-]", '', text)
        
        # Tokenize
        tokens = word_tokenize(text)
        
        # Remove stopwords and single characters
        stop_words = set(stopwords.words('english'))
        tokens = [token for token in tokens 
                 if token not in stop_words and len(token) > 1 and token.isalpha()]
        
        return tokens

    def _calculate_zipf_metrics(self) -> Dict:
        """
        Calculate Zipf's Law metrics for the text.

        Returns:
            Dictionary containing Zipf's Law metrics
        """
        if not self.ranked_words:
            return {}

        ranks = []
        frequencies = []
        expected_frequencies = []

        for rank, (word, freq) in enumerate(self.ranked_words[:100], 1):
            ranks.append(rank)
            frequencies.append(freq)
            # Zipf's Law: frequency ≈ constant / rank
            expected_freq = self.ranked_words[0][1] / rank
            expected_frequencies.append(expected_freq)

        # Calculate correlation between actual and expected Zipf distribution
        correlation = self._calculate_correlation(frequencies, expected_frequencies)

        return {
            'top_10_words': self.ranked_words[:10],
            'zipf_correlation': correlation,
            'is_zipfian': correlation > 0.8,  # Strong Zipf distribution if correlation > 0.8
            'distribution_analysis': {
                'rank_1_frequency': self.ranked_words[0][1] if self.ranked_words else 0,
                'avg_frequency': sum(freq for _, freq in self.ranked_words[:10]) / 10,
                'theoretical_vs_actual': list(zip(
                    [freq for _, freq in self.ranked_words[:10]],
                    [self.ranked_words[0][1] / (i+1) for i in range(10)]
                ))
            }
        }

    def _calculate_correlation(self, actual: List[float], expected: List[float]) -> float:
        """
        Calculate Pearson correlation coefficient.

        Args:
            actual: Actual frequencies
            expected: Expected frequencies

        Returns:
            Correlation coefficient between -1 and 1
        """
        if len(actual) < 2:
            return 0.0

        mean_actual = sum(actual) / len(actual)
        mean_expected = sum(expected) / len(expected)

        numerator = sum((actual[i] - mean_actual) * (expected[i] - mean_expected) 
                       for i in range(len(actual)))
        
        denom_actual = sum((x - mean_actual) ** 2 for x in actual)
        denom_expected = sum((x - mean_expected) ** 2 for x in expected)

        if denom_actual == 0 or denom_expected == 0:
            return 0.0

        return numerator / math.sqrt(denom_actual * denom_expected)

    def get_word_percentile(self, word: str) -> Optional[Tuple[int, float]]:
        """
        Get the rank and percentile of a specific word.

        Args:
            word: The word to find

        Returns:
            Tuple of (rank, frequency) or None if word not found
        """
        word = word.lower()
        for rank, (w, freq) in enumerate(self.ranked_words, 1):
            if w == word:
                percentile = (rank / len(self.ranked_words)) * 100 if self.ranked_words else 0
                return (rank, percentile)
        return None


class ContextualWordAnalyzer:
    """
    Analyzes words within their textual context to extract meanings and relationships.
    """

    def __init__(self):
        """Initialize the contextual word analyzer."""
        self.text = ""
        self.sentences = []
        self.word_contexts = defaultdict(list)

    def analyze_word_context(self, text: str, target_word: Optional[str] = None) -> Dict:
        """
        Analyze words and their contexts within the text.

        Args:
            text: Input text to analyze
            target_word: Specific word to analyze (if None, analyzes all)

        Returns:
            Dictionary containing contextual analysis
        """
        self.text = text
        self.sentences = sent_tokenize(text)
        
        # Extract context for words
        self._extract_word_contexts()
        
        # Analyze relationships
        if target_word:
            return self._analyze_specific_word(target_word)
        else:
            return self._analyze_all_significant_words()

    def _extract_word_contexts(self) -> None:
        """Extract sentences containing each word."""
        stop_words = set(stopwords.words('english'))
        
        for sentence in self.sentences:
            tokens = word_tokenize(sentence.lower())
            tokens = [t for t in tokens if t.isalpha()]
            
            for token in tokens:
                if token not in stop_words and len(token) > 2:
                    self.word_contexts[token].append(sentence)

    def _analyze_specific_word(self, word: str) -> Dict:
        """
        Analyze a specific word and its contexts.

        Args:
            word: The word to analyze

        Returns:
            Detailed contextual analysis of the word
        """
        word = word.lower()
        contexts = self.word_contexts.get(word, [])
        
        if not contexts:
            return {
                'word': word,
                'found': False,
                'message': f"Word '{word}' not found in text"
            }

        # Extract POS tag
        tagged = pos_tag(word_tokenize(word))
        pos = tagged[0][1] if tagged else 'UNKNOWN'

        # Extract surrounding words
        surrounding_words = self._extract_surrounding_words(word, contexts)

        # Infer meaning from context
        inferred_meaning = self._infer_meaning_from_context(word, contexts)

        return {
            'word': word,
            'found': True,
            'frequency': len(contexts),
            'part_of_speech': pos,
            'contexts': contexts[:5],  # Return first 5 contexts
            'surrounding_words': surrounding_words,
            'inferred_meaning': inferred_meaning,
            'word_class': self._determine_word_class(word, contexts)
        }

    def _analyze_all_significant_words(self) -> Dict:
        """
        Analyze all significant words in the text.

        Returns:
            Analysis of the most significant words
        """
        # Filter words by frequency
        word_frequencies = Counter()
        stop_words = set(stopwords.words('english'))
        
        for sentence in self.sentences:
            tokens = word_tokenize(sentence.lower())
            tokens = [t for t in tokens if t.isalpha() and t not in stop_words and len(t) > 2]
            word_frequencies.update(tokens)

        # Analyze top words
        significant_words = {}
        for word, freq in word_frequencies.most_common(20):
            contexts = self.word_contexts.get(word, [])
            inferred_meaning = self._infer_meaning_from_context(word, contexts)
            
            significant_words[word] = {
                'frequency': freq,
                'contexts_count': len(contexts),
                'inferred_meaning': inferred_meaning
            }

        return {
            'total_unique_words': len(word_frequencies),
            'significant_words': significant_words,
            'text_summary': {
                'total_sentences': len(self.sentences),
                'avg_sentence_length': len(self.text.split()) / len(self.sentences) if self.sentences else 0
            }
        }

    def _extract_surrounding_words(self, target_word: str, contexts: List[str]) -> Dict[str, int]:
        """
        Extract words that frequently appear near the target word.

        Args:
            target_word: The word to find neighbors for
            contexts: Sentences containing the word

        Returns:
            Dictionary of surrounding words and their frequencies
        """
        surrounding = Counter()
        stop_words = set(stopwords.words('english'))
        
        for context in contexts:
            tokens = word_tokenize(context.lower())
            
            # Find target word position
            for i, token in enumerate(tokens):
                if token == target_word:
                    # Get surrounding words (within 3 words)
                    start = max(0, i - 3)
                    end = min(len(tokens), i + 4)
                    
                    for j in range(start, end):
                        if j != i and tokens[j].isalpha():
                            surrounding[tokens[j]] += 1

        # Filter stopwords
        return {word: count for word, count in surrounding.most_common(15) 
                if word not in stop_words}

    def _infer_meaning_from_context(self, word: str, contexts: List[str]) -> Dict:
        """
        Infer the meaning of a word from its contexts.

        Args:
            word: The word to analyze
            contexts: Sentences containing the word

        Returns:
            Dictionary with inferred meaning and supporting context
        """
        if not contexts:
            return {'meaning': 'Unknown', 'confidence': 0.0}

        # Analyze contexts for semantic clues
        semantic_indicators = defaultdict(int)
        
        for context in contexts:
            tokens = word_tokenize(context.lower())
            
            # Look for common semantic patterns
            if any(verb in tokens for verb in ['is', 'are', 'was', 'were', 'being']):
                semantic_indicators['descriptive'] += 1
            
            if any(verb in tokens for verb in ['do', 'does', 'did', 'doing']):
                semantic_indicators['action'] += 1
            
            if any(preposition in tokens for preposition in ['in', 'on', 'at', 'with']):
                semantic_indicators['relational'] += 1

        # Determine most likely word type
        if semantic_indicators:
            primary_type = max(semantic_indicators, key=semantic_indicators.get)
            confidence = semantic_indicators[primary_type] / len(contexts)
        else:
            primary_type = 'unknown'
            confidence = 0.0

        return {
            'primary_usage': primary_type,
            'confidence': min(confidence, 1.0),
            'context_count': len(contexts),
            'semantic_indicators': dict(semantic_indicators)
        }

    def _determine_word_class(self, word: str, contexts: List[str]) -> str:
        """
        Determine the grammatical class of the word.

        Args:
            word: The word to classify
            contexts: Sentences containing the word

        Returns:
            Grammatical class of the word
        """
        pos_tags = Counter()
        
        for context in contexts:
            tagged = pos_tag(word_tokenize(context.lower()))
            for token, pos in tagged:
                if token == word:
                    pos_tags[pos] += 1

        if pos_tags:
            most_common_pos = pos_tags.most_common(1)[0][0]
            return self._map_pos_to_class(most_common_pos)
        
        return 'Unknown'

    @staticmethod
    def _map_pos_to_class(pos_tag: str) -> str:
        """
        Map NLTK POS tags to readable word classes.

        Args:
            pos_tag: NLTK POS tag

        Returns:
            Readable word class
        """
        pos_mapping = {
            'NN': 'Noun',
            'NNS': 'Noun (Plural)',
            'NNP': 'Proper Noun',
            'NNPS': 'Proper Noun (Plural)',
            'VB': 'Verb',
            'VBD': 'Verb (Past)',
            'VBG': 'Verb (Gerund)',
            'VBN': 'Verb (Past Participle)',
            'VBP': 'Verb (Present)',
            'VBZ': 'Verb (3rd Person Singular)',
            'JJ': 'Adjective',
            'JJR': 'Adjective (Comparative)',
            'JJS': 'Adjective (Superlative)',
            'RB': 'Adverb',
            'RBR': 'Adverb (Comparative)',
            'RBS': 'Adverb (Superlative)',
            'PRP': 'Pronoun',
            'PRP$': 'Pronoun (Possessive)',
            'IN': 'Preposition',
            'CC': 'Conjunction',
            'DT': 'Determiner',
            'CD': 'Cardinal Number',
        }
        return pos_mapping.get(pos_tag, 'Unknown')


class WordAnalyzerIntegration:
    """
    Integrated word analyzer combining Zipf's Law and contextual analysis.
    """

    def __init__(self):
        """Initialize the integrated analyzer."""
        self.zipf_analyzer = ZipfsLawAnalyzer()
        self.context_analyzer = ContextualWordAnalyzer()

    def analyze_text(self, text: str, target_word: Optional[str] = None) -> Dict:
        """
        Perform complete analysis of text using both Zipf's Law and contextual analysis.

        Args:
            text: Input text to analyze
            target_word: Specific word to focus on (optional)

        Returns:
            Comprehensive analysis combining both approaches
        """
        # Zipf's Law analysis
        zipf_results = self.zipf_analyzer.analyze_text(text)
        
        # Contextual analysis
        context_results = self.context_analyzer.analyze_word_context(text, target_word)
        
        return {
            'zipf_analysis': zipf_results,
            'contextual_analysis': context_results,
            'combined_insights': self._generate_insights(zipf_results, context_results)
        }

    def _generate_insights(self, zipf_results: Dict, context_results: Dict) -> Dict:
        """
        Generate combined insights from both analyses.

        Args:
            zipf_results: Results from Zipf's Law analysis
            context_results: Results from contextual analysis

        Returns:
            Combined insights and recommendations
        """
        return {
            'text_complexity': self._assess_complexity(zipf_results),
            'vocabulary_richness': zipf_results['unique_words'] / max(zipf_results['total_words'], 1),
            'dominant_topics': [word for word, _ in zipf_results.get('ranked_words', [])[:10]],
            'recommended_focus_words': self._recommend_focus_words(zipf_results, context_results)
        }

    @staticmethod
    def _assess_complexity(zipf_results: Dict) -> str:
        """
        Assess text complexity based on Zipf's Law metrics.

        Args:
            zipf_results: Results from Zipf's Law analysis

        Returns:
            Text complexity assessment
        """
        zipf_correlation = zipf_results.get('zipf_metrics', {}).get('zipf_correlation', 0)
        
        if zipf_correlation > 0.9:
            return 'Simple/Formulaic'
        elif zipf_correlation > 0.8:
            return 'Normal'
        elif zipf_correlation > 0.7:
            return 'Complex/Specialized'
        else:
            return 'Very Complex/Irregular'

    @staticmethod
    def _recommend_focus_words(zipf_results: Dict, context_results: Dict) -> List[str]:
        """
        Recommend which words to focus on for learning.

        Args:
            zipf_results: Results from Zipf's Law analysis
            context_results: Results from contextual analysis

        Returns:
            List of recommended focus words
        """
        # Recommend words that are:
        # 1. Frequent enough to be important (rank < 50)
        # 2. Not in top 10 (common words)
        # 3. Have diverse contexts (appear in multiple different sentences)
        
        focus_words = []
        top_words = [word for word, _ in zipf_results.get('ranked_words', [])[10:50]]
        
        for word in top_words[:10]:
            focus_words.append(word)
        
        return focus_words
