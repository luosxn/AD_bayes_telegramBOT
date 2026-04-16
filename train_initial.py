#!/usr/bin/env python3
"""
初始训练脚本
用于提供一些基础的垃圾消息和正常消息样本
"""
from bayes_classifier import get_classifier
from models import init_db, add_training_data
from loguru import logger

# 初始垃圾消息样本（广告类）
INITIAL_SPAM_SAMPLES = [
    # 服务器/CDN广告
    "🔥 国内 - 海外 服务器 免备案 大带宽 欢迎业务 🌍 CDN加速网站 高防 过移动屏蔽 🔴 直播 推拉流 稳定 大带宽 不限制流量 🛠️ 搭建 专业定制开发app 🔥🔥 📱 销售：@cdncloud001 📢 频道： @xxxx",
    "一手出 微信 QQ 支付宝 抖音 京东 淘宝 WS 火种 手机卡 电销卡 流量卡 需要联系唯一客服飞机： @xxxx01 双向 @xxxx_bot",
    "境外CDN加速，免备案服务器，大带宽不限流量，联系 @admin",
    "国内海外服务器租用，免备案，高防CDN，联系QQ：123456789",
    
    # 兼职/赚钱广告
    "有淘宝京东闲鱼抖音购物软件的兄弟来找我干活 一单一结280秒结 @xxxx21",
    "招聘兼职，日赚300-500，手机操作，无需押金，联系 @parttime",
    "网络兼职，刷单返利，一单5-10元，多劳多得，加群了解",
    "招代理，零门槛，月入过万，详情私聊 @agent",
    
    # 金融/投资广告
    "外汇黄金投资，专业导师带单，稳赚不赔，开户送金 @forex",
    "股票推荐，内幕消息，跟庄操作，保证收益，联系 @stock",
    "数字货币交易，杠杆合约，百倍收益，注册送USDT",
    "网贷下款快，无视黑白，秒批秒到，联系 @loan",
    
    # 赌博/博彩广告
    "线上博彩，真人娱乐，注册送彩金，提现秒到 @casino",
    "彩票预测，百分百中奖，跟单必赚，联系 @lottery",
    "棋牌游戏，牛牛金花，24小时在线，充值优惠",
    
    # 账号/数据交易
    "出售微信老号，实名认证，安全稳定，联系 @seller",
    "抖音粉丝号，万粉千粉，真人活跃，价格优惠",
    "企业数据，精准客户资源，按行业分类，需要联系",
    "银行四件套，全套资料，包过审核，联系 @bank",
    
    # 色情/违规广告
    "同城约炮，美女上门，安全保密，联系 @hookup",
    "高清视频，会员专享，永久更新，联系 @video",
    "裸聊直播，一对一视频，充值观看",
]

# 初始正常消息样本
INITIAL_HAM_SAMPLES = [
    # 日常聊天
    "大家好，今天天气真不错",
    "有人知道这道题怎么做吗？",
    "谢谢分享，很有用",
    "哈哈，笑死我了",
    "周末有什么安排？",
    "这个电影好看吗？",
    "请问有人在线吗？",
    "早上好，各位",
    "晚上一起吃饭吧",
    "收到，谢谢",
    
    # 技术讨论
    "Python怎么安装第三方库？",
    "这个bug怎么解决？",
    "有人用过这个框架吗？",
    "代码报错了，帮忙看看",
    "推荐一个好用的IDE",
    "学习编程从什么开始？",
    "这个问题怎么优化？",
    "求教，这个函数什么意思",
    
    # 生活交流
    "今天吃了什么好吃的？",
    "推荐一家好吃的餐厅",
    "最近有什么好书推荐？",
    "健身打卡第10天",
    "养猫还是养狗好？",
    "旅游攻略求推荐",
    "这个手机怎么样？",
    "求推荐耳机",
]


def train_initial_data():
    """使用初始数据训练模型"""
    logger.info("开始初始训练...")
    
    # 初始化数据库
    init_db()
    
    classifier = get_classifier()
    
    # 训练垃圾消息
    spam_count = 0
    for text in INITIAL_SPAM_SAMPLES:
        classifier.train(text, is_spam=True)
        add_training_data(text, is_spam=True, source='initial')
        spam_count += 1
    logger.info(f"已训练 {spam_count} 条垃圾消息样本")
    
    # 训练正常消息
    ham_count = 0
    for text in INITIAL_HAM_SAMPLES:
        classifier.train(text, is_spam=False)
        add_training_data(text, is_spam=False, source='initial')
        ham_count += 1
    logger.info(f"已训练 {ham_count} 条正常消息样本")
    
    # 保存模型
    classifier.save_model()
    
    # 打印统计
    stats = classifier.get_stats()
    logger.info("初始训练完成！")
    logger.info(f"模型统计: 垃圾={stats['spam_count']}, 正常={stats['ham_count']}, 词汇表={stats['vocab_size']}")


if __name__ == "__main__":
    train_initial_data()
