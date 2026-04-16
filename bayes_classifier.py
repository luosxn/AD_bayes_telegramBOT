"""
贝叶斯垃圾消息分类器
基于朴素贝叶斯算法实现，支持中文分词
"""
import re
import pickle
import math
from collections import defaultdict
from typing import Dict, List, Tuple, Optional
from pathlib import Path
import jieba
from loguru import logger


class BayesClassifier:
    """朴素贝叶斯分类器"""

    def __init__(self, model_path: str = "./data/bayes_model.pkl"):
        self.model_path = Path(model_path)
        self.model_path.parent.mkdir(parents=True, exist_ok=True)

        # 词频统计
        self.spam_words: Dict[str, int] = defaultdict(int)  # 垃圾消息词频
        self.ham_words: Dict[str, int] = defaultdict(int)   # 正常消息词频

        # 文档计数
        self.spam_count: int = 0  # 垃圾消息数量
        self.ham_count: int = 0   # 正常消息数量
        self.total_count: int = 0  # 总消息数量

        # 词汇表
        self.vocab: set = set()

        # 平滑参数
        self.alpha: float = 1.0  # 拉普拉斯平滑

        self._load_model()

    def _tokenize(self, text: str) -> List[str]:
        """中文分词"""
        # 清理文本
        text = self._clean_text(text)
        # 使用jieba分词
        words = jieba.lcut(text)
        # 过滤停用词和短词
        words = [w.strip().lower() for w in words if len(w.strip()) > 1]
        return words

    def _clean_text(self, text: str) -> str:
        """清理文本"""
        # 移除URL
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        # 移除特殊字符但保留中文、英文、数字
        text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9\s]', ' ', text)
        # 合并多个空格
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def train(self, text: str, is_spam: bool) -> None:
        """训练模型"""
        words = self._tokenize(text)

        if is_spam:
            self.spam_count += 1
            for word in words:
                self.spam_words[word] += 1
                self.vocab.add(word)
        else:
            self.ham_count += 1
            for word in words:
                self.ham_words[word] += 1
                self.vocab.add(word)

        self.total_count += 1
        logger.debug(f"训练样本: {'垃圾' if is_spam else '正常'}消息, 词数: {len(words)}")

    def predict(self, text: str) -> Tuple[bool, float]:
        """
        预测消息是否为垃圾消息
        返回: (是否为垃圾消息, 置信度)
        """
        if self.total_count == 0:
            return False, 0.0

        words = self._tokenize(text)
        if not words:
            return False, 0.0

        # 计算先验概率
        p_spam = (self.spam_count + self.alpha) / (self.total_count + 2 * self.alpha)
        p_ham = (self.ham_count + self.alpha) / (self.total_count + 2 * self.alpha)

        # 计算对数概率（避免下溢）
        log_p_spam = math.log(p_spam)
        log_p_ham = math.log(p_ham)

        # 垃圾消息总词数
        spam_total = sum(self.spam_words.values())
        # 正常消息总词数
        ham_total = sum(self.ham_words.values())

        vocab_size = len(self.vocab)

        for word in words:
            # 计算条件概率（带拉普拉斯平滑）
            spam_word_count = self.spam_words.get(word, 0)
            ham_word_count = self.ham_words.get(word, 0)

            # P(word|spam)
            p_word_given_spam = (spam_word_count + self.alpha) / (spam_total + self.alpha * vocab_size)
            # P(word|ham)
            p_word_given_ham = (ham_word_count + self.alpha) / (ham_total + self.alpha * vocab_size)

            log_p_spam += math.log(p_word_given_spam)
            log_p_ham += math.log(p_word_given_ham)

        # 使用softmax转换回概率
        max_log = max(log_p_spam, log_p_ham)
        exp_spam = math.exp(log_p_spam - max_log)
        exp_ham = math.exp(log_p_ham - max_log)

        p_spam_given_text = exp_spam / (exp_spam + exp_ham)

        is_spam = p_spam_given_text > 0.5
        confidence = p_spam_given_text

        return is_spam, confidence

    def save_model(self) -> None:
        """保存模型到文件"""
        model_data = {
            'spam_words': dict(self.spam_words),
            'ham_words': dict(self.ham_words),
            'spam_count': self.spam_count,
            'ham_count': self.ham_count,
            'total_count': self.total_count,
            'vocab': self.vocab
        }
        with open(self.model_path, 'wb') as f:
            pickle.dump(model_data, f)
        logger.info(f"模型已保存到 {self.model_path}")

    def _load_model(self) -> None:
        """从文件加载模型"""
        if self.model_path.exists():
            try:
                with open(self.model_path, 'rb') as f:
                    model_data = pickle.load(f)
                self.spam_words = defaultdict(int, model_data['spam_words'])
                self.ham_words = defaultdict(int, model_data['ham_words'])
                self.spam_count = model_data['spam_count']
                self.ham_count = model_data['ham_count']
                self.total_count = model_data['total_count']
                self.vocab = model_data['vocab']
                logger.info(f"模型已从 {self.model_path} 加载")
            except Exception as e:
                logger.error(f"加载模型失败: {e}")
        else:
            logger.info("未找到现有模型，将创建新模型")

    def get_stats(self) -> Dict:
        """获取模型统计信息"""
        return {
            'spam_count': self.spam_count,
            'ham_count': self.ham_count,
            'total_count': self.total_count,
            'vocab_size': len(self.vocab),
            'spam_words': len(self.spam_words),
            'ham_words': len(self.ham_words)
        }


# 全局分类器实例
_classifier: Optional[BayesClassifier] = None


def get_classifier() -> BayesClassifier:
    """获取分类器单例"""
    global _classifier
    if _classifier is None:
        _classifier = BayesClassifier()
    return _classifier
