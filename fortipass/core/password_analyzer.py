#!/usr/bin/env python3
# FortiPass - Password Analyzer Core Module

import math
import re
import os
from datetime import datetime
from typing import Dict, List, Tuple, Any

class PasswordAnalyzer:
    """
    Core password analysis engine following NIST SP 800-63B guidelines.
    Performs entropy calculation, pattern detection, and strength assessment.
    """
    
    def __init__(self, wordlist_path: str = None):
        """
        Initialize the password analyzer with optional wordlist for dictionary checks.
        
        Args:
            wordlist_path: Path to the dictionary file of common passwords
        """
        self.common_words = set()
        self.keyboard_patterns = [
            "qwerty", "asdfgh", "zxcvbn", "1234", "qazwsx",
            "poiuyt", "lkjhgf", "mnbvcx", "0987", "wsxcde"
        ]
        
        # Load common password dictionary if provided
        if wordlist_path and os.path.exists(wordlist_path):
            with open(wordlist_path, 'r', encoding='utf-8', errors='ignore') as f:
                self.common_words = {line.strip().lower() for line in f if line.strip()}
    
    def analyze(self, password: str) -> Dict[str, Any]:
        """
        Perform comprehensive password analysis.
        
        Args:
            password: The password to analyze
            
        Returns:
            Dictionary containing analysis results
        """
        if not password:
            return self._empty_result()
        
        # Basic metrics
        length = len(password)
        entropy = self._calculate_entropy(password)
        
        # Character diversity checks
        has_lowercase = bool(re.search(r'[a-z]', password))
        has_uppercase = bool(re.search(r'[A-Z]', password))
        has_digits = bool(re.search(r'[0-9]', password))
        has_symbols = bool(re.search(r'[^a-zA-Z0-9\s]', password))
        char_diversity = sum([has_lowercase, has_uppercase, has_digits, has_symbols])
        
        # Pattern detection
        patterns = self._detect_patterns(password)
        
        # Calculate strength score (0-100)
        strength_score = self._calculate_strength(
            length, entropy, char_diversity, patterns
        )
        
        # Calculate crack time estimation
        crack_time = self._estimate_crack_time(entropy)
        
        # Generate feedback
        feedback = self._generate_feedback(
            length, entropy, char_diversity, patterns, password
        )
        
        return {
            "length": length,
            "entropy": entropy,
            "char_diversity": char_diversity,
            "has_lowercase": has_lowercase,
            "has_uppercase": has_uppercase,
            "has_digits": has_digits,
            "has_symbols": has_symbols,
            "patterns": patterns,
            "strength_score": strength_score,
            "strength_category": self._get_strength_category(strength_score),
            "crack_time": crack_time,
            "feedback": feedback
        }
    
    def _empty_result(self) -> Dict[str, Any]:
        """Return default result for empty password."""
        return {
            "length": 0,
            "entropy": 0,
            "char_diversity": 0,
            "has_lowercase": False,
            "has_uppercase": False,
            "has_digits": False,
            "has_symbols": False,
            "patterns": [],
            "strength_score": 0,
            "strength_category": "Very Weak",
            "crack_time": "Instant",
            "feedback": ["Password cannot be empty"]
        }
    
    def _calculate_entropy(self, password: str) -> float:
        """
        Calculate Shannon entropy of the password.
        
        H = -sum(p_i * log2(p_i)) where p_i is the probability of character i
        """
        if not password:
            return 0
            
        # Count character frequencies
        char_count = {}
        for char in password:
            if char in char_count:
                char_count[char] += 1
            else:
                char_count[char] = 1
        
        # Calculate entropy
        length = len(password)
        entropy = 0
        for count in char_count.values():
            probability = count / length
            entropy -= probability * math.log2(probability)
            
        # Adjust for password length
        entropy *= length
        
        return round(entropy, 2)
    
    def _detect_patterns(self, password: str) -> List[Dict[str, Any]]:
        """
        Detect common patterns that weaken passwords.
        
        Returns:
            List of detected patterns with type and description
        """
        patterns = []
        password_lower = password.lower()
        
        # Check for dictionary words
        if self.common_words and password_lower in self.common_words:
            patterns.append({
                "type": "dictionary_word",
                "description": "Common password",
                "severity": "high"
            })
        
        # Check for dates (common formats)
        date_patterns = [
            r'19\d{2}', r'20\d{2}',  # Years (1900-2099)
            r'0[1-9]|1[0-2][0-3][0-9]',  # MMDD
            r'[0-3][0-9][0-1][0-9]',  # DDMM
        ]
        
        for pattern in date_patterns:
            if re.search(pattern, password):
                patterns.append({
                    "type": "date",
                    "description": "Contains date pattern",
                    "severity": "medium"
                })
                break
        
        # Check for keyboard patterns
        for pattern in self.keyboard_patterns:
            if pattern in password_lower:
                patterns.append({
                    "type": "keyboard_pattern",
                    "description": f"Keyboard pattern: '{pattern}'",
                    "severity": "high"
                })
        
        # Check for repeated characters
        if re.search(r'(.)\1{2,}', password):
            patterns.append({
                "type": "repeated_chars",
                "description": "Repeated characters",
                "severity": "medium"
            })
        
        # Check for sequential characters
        if re.search(r'(abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz|012|123|234|345|456|567|678|789|890)', password_lower):
            patterns.append({
                "type": "sequential_chars",
                "description": "Sequential characters",
                "severity": "medium"
            })
        
        # Check for repeated sequences
        if re.search(r'(.{2,})\1+', password):
            patterns.append({
                "type": "repeated_sequence",
                "description": "Repeated sequence of characters",
                "severity": "medium"
            })
            
        return patterns
    
    def _calculate_strength(self, length: int, entropy: float, 
                           char_diversity: int, patterns: List[Dict]) -> int:
        """
        Calculate password strength score (0-100).
        
        Args:
            length: Password length
            entropy: Shannon entropy
            char_diversity: Number of character classes used
            patterns: List of detected weakness patterns
            
        Returns:
            Integer score from 0-100
        """
        # Base score from entropy
        score = min(100, entropy * 4)
        
        # Adjust for length
        if length < 8:
            score -= (8 - length) * 10
        elif length > 12:
            score += min(20, (length - 12) * 2)
        
        # Adjust for character diversity
        if char_diversity < 3:
            score -= (3 - char_diversity) * 10
        elif char_diversity == 4:
            score += 10
            
        # Penalize for patterns
        pattern_penalty = 0
        for pattern in patterns:
            if pattern["severity"] == "high":
                pattern_penalty += 25
            elif pattern["severity"] == "medium":
                pattern_penalty += 15
            else:
                pattern_penalty += 5
                
        score = max(0, score - pattern_penalty)
        
        return round(min(100, max(0, score)))
    
    def _get_strength_category(self, score: int) -> str:
        """Convert numeric score to categorical strength."""
        if score < 20:
            return "Very Weak"
        elif score < 40:
            return "Weak"
        elif score < 60:
            return "Moderate"
        elif score < 80:
            return "Strong"
        else:
            return "Very Strong"
    
    def _estimate_crack_time(self, entropy: float) -> str:
        """
        Estimate password cracking time based on entropy.
        
        Assumes modern hardware capabilities (2023) for offline attacks.
        """
        # Calculations based on 100 billion guesses per second (high-end hardware)
        if entropy <= 0:
            return "Instant"
            
        # Estimate seconds to crack based on entropy
        # 2^entropy / guesses_per_second
        seconds = 2 ** entropy / (10 ** 11)
        
        if seconds < 1:
            return "Instant"
        elif seconds < 60:
            return f"{round(seconds)} seconds"
        elif seconds < 3600:
            return f"{round(seconds / 60)} minutes"
        elif seconds < 86400:
            return f"{round(seconds / 3600)} hours"
        elif seconds < 2592000:  # 30 days
            return f"{round(seconds / 86400)} days"
        elif seconds < 31536000:  # 1 year
            return f"{round(seconds / 2592000)} months"
        elif seconds < 315360000:  # 10 years
            return f"{round(seconds / 31536000)} years"
        elif seconds < 3153600000:  # 100 years
            return f"{round(seconds / 31536000)} years"
        else:
            return "Centuries"
    
    def _generate_feedback(self, length: int, entropy: float, 
                          char_diversity: int, patterns: List[Dict],
                          password: str) -> List[str]:
        """Generate actionable feedback for password improvement."""
        feedback = []
        
        # Length feedback
        if length < 8:
            feedback.append("Password is too short. Use at least 8 characters.")
        elif length < 12:
            feedback.append("Consider using a longer password (12+ characters).")
        
        # Character diversity feedback
        missing_classes = []
        if not re.search(r'[a-z]', password):
            missing_classes.append("lowercase letters")
        if not re.search(r'[A-Z]', password):
            missing_classes.append("uppercase letters")
        if not re.search(r'[0-9]', password):
            missing_classes.append("numbers")
        if not re.search(r'[^a-zA-Z0-9\s]', password):
            missing_classes.append("special characters")
            
        if missing_classes:
            feedback.append(f"Add {', '.join(missing_classes)} to increase strength.")
        
        # Pattern-based feedback
        for pattern in patterns:
            if pattern["type"] == "dictionary_word":
                feedback.append("Avoid using common passwords or dictionary words.")
            elif pattern["type"] == "date":
                feedback.append("Avoid using dates in your password.")
            elif pattern["type"] == "keyboard_pattern":
                feedback.append("Avoid keyboard patterns like 'qwerty' or 'asdfgh'.")
            elif pattern["type"] == "repeated_chars":
                feedback.append("Avoid repeating characters (e.g., 'aaa').")
            elif pattern["type"] == "sequential_chars":
                feedback.append("Avoid sequential characters like 'abc' or '123'.")
            elif pattern["type"] == "repeated_sequence":
                feedback.append("Avoid repeating sequences of characters.")
        
        # General improvement suggestions
        if entropy < 50:
            feedback.append("Consider using a passphrase with multiple words.")
            
        if not feedback:
            feedback.append("Password meets security requirements.")
            
        return feedback
        
    def generate_strong_password(self, length: int = 16, 
                                include_uppercase: bool = True,
                                include_digits: bool = True,
                                include_symbols: bool = True) -> str:
        """
        Generate a cryptographically strong password.
        
        Args:
            length: Password length
            include_uppercase: Include uppercase letters
            include_digits: Include digits
            include_symbols: Include special symbols
            
        Returns:
            Strong generated password
        """
        import secrets
        import string
        
        # Define character sets
        chars = string.ascii_lowercase
        if include_uppercase:
            chars += string.ascii_uppercase
        if include_digits:
            chars += string.digits
        if include_symbols:
            chars += string.punctuation
            
        # Generate password
        password = ''.join(secrets.choice(chars) for _ in range(length))
        
        # Ensure at least one character from each included set
        while True:
            has_lower = any(c in string.ascii_lowercase for c in password)
            has_upper = any(c in string.ascii_uppercase for c in password) if include_uppercase else True
            has_digit = any(c in string.digits for c in password) if include_digits else True
            has_symbol = any(c in string.punctuation for c in password) if include_symbols else True
            
            if has_lower and has_upper and has_digit and has_symbol:
                break
            
            # Regenerate if requirements not met
            password = ''.join(secrets.choice(chars) for _ in range(length))
            
        return password 