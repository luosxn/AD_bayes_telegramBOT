#!/usr/bin/env python3
"""
分类器测试脚本
用于测试贝叶斯分类器的准确性
"""
from bayes_classifier import BayesClassifier


def test_classifier():
    """测试分类器"""
    print("=" * 60)
    print("贝叶斯分类器测试")
    print("=" * 60)

    # 创建新的分类器实例（不加载已有模型）
    classifier = BayesClassifier(model_path="./data/test_model.pkl")

    # 训练数据
    spam_samples = [
        "出售微信号，老号稳定，联系 @seller",
        "兼职赚钱，日入300，联系 @parttime",
        "服务器租用，免备案，联系 @hosting",
        "投资理财，稳赚不赔，联系 @invest",
        "博彩娱乐，注册送彩金，联系 @casino",
    ]

    ham_samples = [
        "大家好，今天天气不错",
        "这个代码怎么写？",
        "谢谢分享",
        "晚上吃什么？",
        "周末有什么安排",
    ]

    print("\n1. 训练模型...")
    for text in spam_samples:
        classifier.train(text, is_spam=True)
        print(f"  [垃圾] {text[:30]}...")

    for text in ham_samples:
        classifier.train(text, is_spam=False)
        print(f"  [正常] {text[:30]}...")

    print(f"\n训练完成！")
    stats = classifier.get_stats()
    print(f"  垃圾样本: {stats['spam_count']}")
    print(f"  正常样本: {stats['ham_count']}")
    print(f"  词汇表大小: {stats['vocab_size']}")

    # 测试数据
    test_cases = [
        ("出售QQ号，联系 @qqseller", True),
        ("兼职招聘，日赚500", True),
        ("服务器大带宽，免备案", True),
        ("今天天气真好啊", False),
        ("这个bug怎么解决？", False),
        ("谢谢你的帮助", False),
    ]

    print("\n2. 测试预测...")
    print("-" * 60)

    correct = 0
    for text, expected in test_cases:
        is_spam, confidence = classifier.predict(text)
        result = "✓" if is_spam == expected else "✗"
        label = "垃圾" if is_spam else "正常"
        expected_label = "垃圾" if expected else "正常"
        print(f"{result} [{label}] 置信度:{confidence:.2%} | {text[:30]}...")
        print(f"   预期: {expected_label}")
        if is_spam == expected:
            correct += 1

    print("-" * 60)
    accuracy = correct / len(test_cases) * 100
    print(f"准确率: {correct}/{len(test_cases)} ({accuracy:.1f}%)")

    # 保存测试模型
    classifier.save_model()
    print("\n测试模型已保存")

    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)


if __name__ == "__main__":
    test_classifier()
