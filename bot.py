"""
Telegram Bot 主程序
实现消息处理、命令处理和垃圾消息拦截功能
"""
import asyncio
import sys
from typing import Optional

from telegram import Update, ChatMember, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand, BotCommandScopeAllPrivateChats, BotCommandScopeAllGroupChats
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
    ChatMemberHandler
)
from telegram.constants import ChatMemberStatus, ChatType
from loguru import logger

from config import get_settings
from bayes_classifier import get_classifier
from models import (
    init_db, add_training_data, add_banned_user, add_user_violation,
    get_banned_users, unban_user, get_user_violation_count, get_training_data,
    get_or_create_group_settings, get_user_violations
)

# 配置日志
settings = get_settings()
logger.remove()
logger.add(sys.stderr, level=settings.log_level)
logger.add("logs/bot.log", rotation="10 MB", retention="7 days", level="INFO")


class SpamBot:
    """垃圾消息拦截机器人"""

    def __init__(self):
        self.classifier = get_classifier()
        self.application: Optional[Application] = None

    async def start(self):
        """启动机器人"""
        # 初始化数据库
        init_db()
        logger.info("数据库初始化完成")

        # 创建应用
        self.application = Application.builder().token(settings.bot_token).build()

        # 注册处理器
        self._register_handlers()

        # 启动机器人
        logger.info("机器人启动中...")
        await self.application.initialize()

        # 设置命令菜单
        await self.setup_commands()

        await self.application.start()
        await self.application.updater.start_polling(drop_pending_updates=True)

        logger.info("机器人已启动，正在运行...")

        # 保持运行
        while True:
            await asyncio.sleep(1)

    def _register_handlers(self):
        """注册消息处理器"""
        # 命令处理器
        self.application.add_handler(CommandHandler("start", self.cmd_start))
        self.application.add_handler(CommandHandler("help", self.cmd_help))
        self.application.add_handler(CommandHandler("markspam", self.cmd_markspam))
        self.application.add_handler(CommandHandler("listbanuser", self.cmd_listbanuser))
        self.application.add_handler(CommandHandler("listspam", self.cmd_listspam))
        self.application.add_handler(CommandHandler("feedspam", self.cmd_feedspam))
        self.application.add_handler(CommandHandler("stats", self.cmd_stats))
        self.application.add_handler(CommandHandler("unban", self.cmd_unban))

        # 回调查询处理器
        self.application.add_handler(CallbackQueryHandler(self.handle_callback))

        # 消息处理器（只处理群组文本消息）
        self.application.add_handler(
            MessageHandler(
                filters.TEXT & filters.ChatType.GROUPS & ~filters.COMMAND,
                self.handle_group_message
            )
        )

        # 机器人被添加到群组/状态变化处理器
        self.application.add_handler(ChatMemberHandler(self.handle_chat_member_update, ChatMemberHandler.MY_CHAT_MEMBER))

        # 错误处理器
        self.application.add_error_handler(self.error_handler)

    async def setup_commands(self):
        """设置机器人命令菜单"""
        try:
            # 私聊命令（所有用户）
            private_commands = [
                BotCommand("start", "开始使用机器人"),
                BotCommand("help", "查看帮助信息"),
                BotCommand("feedspam", "投喂垃圾消息训练"),
                BotCommand("stats", "查看统计信息"),
            ]

            # 群组命令（管理员和普通用户）
            group_commands = [
                BotCommand("start", "开始使用机器人"),
                BotCommand("help", "查看帮助信息"),
                BotCommand("markspam", "标记垃圾消息并封禁用户"),
                BotCommand("listbanuser", "查看封禁用户列表"),
                BotCommand("listspam", "查看垃圾消息列表"),
                BotCommand("feedspam", "投喂垃圾消息训练"),
                BotCommand("stats", "查看统计信息"),
                BotCommand("unban", "解封用户"),
            ]

            # 设置私聊命令
            await self.application.bot.set_my_commands(
                private_commands,
                scope=BotCommandScopeAllPrivateChats()
            )

            # 设置群组命令
            await self.application.bot.set_my_commands(
                group_commands,
                scope=BotCommandScopeAllGroupChats()
            )

            logger.info("机器人命令菜单已设置")
        except Exception as e:
            logger.error(f"设置命令菜单失败: {e}")

    async def handle_chat_member_update(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理机器人被添加到群组或权限变化"""
        if not update.my_chat_member:
            return

        chat_member = update.my_chat_member
        chat = chat_member.chat
        new_status = chat_member.new_chat_member.status
        old_status = chat_member.old_chat_member.status

        # 机器人被添加到群组
        if old_status in [ChatMemberStatus.LEFT, ChatMemberStatus.KICKED] and \
           new_status in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR]:
            logger.info(f"机器人被添加到群组: {chat.title} (ID: {chat.id})")

            # 保存群组设置
            get_or_create_group_settings(chat.id, chat.title)

            # 发送欢迎消息
            welcome_msg = """
🤖 <b>感谢添加贝叶斯广告拦截机器人！</b>

我已准备好保护这个群组免受垃圾广告的侵扰。

<b>请确保给予我以下权限：</b>
✅ 删除消息
✅ 封禁用户

<b>快速开始：</b>
• 我会自动检测并删除置信度超过95%的垃圾消息
• 连续发送3次垃圾消息的用户将被自动封禁
• 使用 /help 查看所有命令

<b>训练我：</b>
• 如果漏掉了垃圾消息，回复该消息并发送 /markspam
• 使用 /feedspam 投喂垃圾消息帮助我学习

祝使用愉快！
            """
            try:
                await context.bot.send_message(
                    chat_id=chat.id,
                    text=welcome_msg,
                    parse_mode='HTML'
                )
            except Exception as e:
                logger.warning(f"无法发送欢迎消息到群组 {chat.id}: {e}")

        # 机器人被提升为管理员
        elif old_status == ChatMemberStatus.MEMBER and new_status == ChatMemberStatus.ADMINISTRATOR:
            logger.info(f"机器人在群组 {chat.title} 被提升为管理员")
            try:
                await context.bot.send_message(
                    chat_id=chat.id,
                    text="✅ 谢谢！我现在有了管理员权限，可以开始保护群组了。",
                    parse_mode='HTML'
                )
            except Exception as e:
                logger.warning(f"无法发送权限确认消息: {e}")

        # 机器人被移除群组
        elif new_status in [ChatMemberStatus.LEFT, ChatMemberStatus.KICKED]:
            logger.info(f"机器人被移除群组: {chat.title} (ID: {chat.id})")

    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """/start 命令"""
        welcome_text = """
🤖 <b>贝叶斯广告拦截机器人</b>

我是一个基于贝叶斯算法的智能广告拦截机器人，可以通过学习自动识别垃圾消息。

<b>主要功能：</b>
• 🛡️ 自动识别并删除垃圾广告
• 📚 通过投喂训练自主学习
• 👮 违规用户自动封禁
• 📊 实时模型更新

<b>使用方法：</b>
1. 将我添加到群组
2. 给予我管理员权限（删除消息、封禁用户）
3. 我会自动开始工作

<b>可用命令：</b>
/markspam - 标记垃圾消息并封禁用户
/listbanuser - 查看封禁用户列表
/listspam - 查看被标记的垃圾消息
/feedspam - 投喂垃圾消息进行训练
/stats - 查看统计信息
/help - 查看帮助

<b>提示：</b>
• 垃圾消息置信度超过 95% 才会被自动删除
• 连续违规 3 次将被自动封禁
• 所有群组共享同一个训练模型
        """
        await update.message.reply_text(welcome_text, parse_mode='HTML')

    async def cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """/help 命令"""
        help_text = """
<b>📖 命令帮助</b>

<b>管理员命令：</b>
/markspam - 回复某条消息使用此命令，标记为垃圾消息并封禁用户
/listbanuser - 查看封禁用户列表，可解封用户
/listspam - 查看被标记的垃圾消息列表，可标记为正常
/unban - 解封用户（回复用户消息或提供用户ID）

<b>普通命令：</b>
/feedspam &lt;文本&gt; - 投喂垃圾消息进行训练（可在私聊中使用）
/stats - 查看机器人和模型统计信息

<b>自动功能：</b>
• 自动检测并删除垃圾消息
• 违规用户自动封禁
• 实时模型更新

<b>注意事项：</b>
• 需要管理员权限才能使用管理命令
• 机器人需要删除消息和封禁用户的权限
• 投喂的训练数据会立即更新模型
        """
        await update.message.reply_text(help_text, parse_mode='HTML')

    async def cmd_markspam(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """/markspam 命令 - 标记垃圾消息"""
        if not update.message or not update.message.reply_to_message:
            await update.message.reply_text(
                "❌ 请回复一条消息来使用此命令\n用法: 回复垃圾消息 + /markspam"
            )
            return

        # 检查权限
        if not await self._is_admin(update, context):
            await update.message.reply_text("❌ 只有管理员可以使用此命令")
            return

        target_msg = update.message.reply_to_message
        chat_id = update.effective_chat.id
        user_id = target_msg.from_user.id

        # 获取消息文本
        text = target_msg.text or target_msg.caption or ""
        if not text:
            await update.message.reply_text("❌ 无法获取消息文本")
            return

        try:
            # 1. 删除原消息
            await context.bot.delete_message(chat_id=chat_id, message_id=target_msg.message_id)

            # 2. 封禁用户
            await context.bot.ban_chat_member(chat_id=chat_id, user_id=user_id)

            # 3. 添加到训练数据（高置信度）
            add_training_data(
                text=text,
                is_spam=True,
                source='manual',
                chat_id=chat_id,
                message_id=target_msg.message_id,
                user_id=user_id
            )

            # 4. 训练模型
            self.classifier.train(text, is_spam=True)
            self.classifier.save_model()

            # 5. 记录封禁
            add_banned_user(
                user_id=user_id,
                chat_id=chat_id,
                username=target_msg.from_user.username,
                first_name=target_msg.from_user.first_name,
                reason="管理员标记为垃圾消息",
                banned_by=update.effective_user.id
            )

            # 6. 记录违规
            add_user_violation(
                user_id=user_id,
                chat_id=chat_id,
                message_text=text[:500],
                confidence=1.0,
                is_banned=True
            )

            await update.message.reply_text(
                f"✅ 已处理垃圾消息\n"
                f"👤 用户: {target_msg.from_user.first_name} (ID: {user_id})\n"
                f"📝 消息已删除\n"
                f"🚫 用户已被封禁\n"
                f"📚 已添加到训练数据"
            )
            logger.info(f"管理员 {update.effective_user.id} 标记消息为垃圾消息并封禁用户 {user_id}")

        except Exception as e:
            logger.error(f"处理markspam命令时出错: {e}")
            await update.message.reply_text(f"❌ 处理失败: {str(e)}")

    async def cmd_listbanuser(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """/listbanuser 命令 - 查看封禁用户列表"""
        if not await self._is_admin(update, context):
            await update.message.reply_text("❌ 只有管理员可以使用此命令")
            return

        chat_id = update.effective_chat.id
        banned_users = get_banned_users(chat_id=chat_id, limit=20)

        if not banned_users:
            await update.message.reply_text("📋 当前没有封禁的用户")
            return

        text = "📋 <b>封禁用户列表</b>\n\n"
        keyboard = []

        for user in banned_users:
            name = user.first_name or user.username or f"用户{user.user_id}"
            date = user.banned_at.strftime("%Y-%m-%d")
            text += f"• {name}\n"
            text += f"  ID: <code>{user.user_id}</code>\n"
            text += f"  封禁时间: {date}\n"
            text += f"  违规次数: {user.violation_count}\n\n"

            # 添加解封按钮
            keyboard.append([
                InlineKeyboardButton(
                    f"解封 {name[:15]}",
                    callback_data=f"unban:{user.user_id}"
                )
            ])

        await update.message.reply_text(
            text,
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def cmd_listspam(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """/listspam 命令 - 查看垃圾消息列表"""
        if not await self._is_admin(update, context):
            await update.message.reply_text("❌ 只有管理员可以使用此命令")
            return

        spam_data = get_training_data(limit=10, is_spam=True)

        if not spam_data:
            await update.message.reply_text("📋 当前没有垃圾消息记录")
            return

        text = "🗑️ <b>最近标记的垃圾消息</b>\n\n"
        keyboard = []

        for i, data in enumerate(spam_data, 1):
            preview = data.text[:100] + "..." if len(data.text) > 100 else data.text
            date = data.created_at.strftime("%Y-%m-%d %H:%M")
            text += f"<b>{i}.</b> {preview}\n"
            text += f"   时间: {date}\n\n"

            keyboard.append([
                InlineKeyboardButton(
                    f"标记 #{i} 为正常",
                    callback_data=f"markham:{data.id}"
                )
            ])

        text += "\n<i>如果发现有误判的消息，请点击按钮标记为正常</i>"

        await update.message.reply_text(
            text,
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def cmd_feedspam(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """/feedspam 命令 - 投喂垃圾消息训练"""
        # 获取命令参数
        args = context.args
        chat_id = update.effective_chat.id

        # 检查是否是回复消息
        if update.message.reply_to_message:
            text = update.message.reply_to_message.text or update.message.reply_to_message.caption or ""
            if not text:
                await update.message.reply_text("❌ 回复的消息没有文本内容")
                return
        elif args:
            text = " ".join(args)
        else:
            await update.message.reply_text(
                "📚 <b>投喂垃圾消息训练</b>\n\n"
                "使用方法:\n"
                "1. 回复一条垃圾消息: <code>/feedspam</code>\n"
                "2. 直接提供文本: <code>/feedspam 这里是垃圾消息内容</code>\n\n"
                "投喂的数据会立即用于训练模型，帮助所有群组更好地识别垃圾消息。",
                parse_mode='HTML'
            )
            return

        try:
            # 添加到训练数据
            add_training_data(
                text=text,
                is_spam=True,
                source='manual',
                chat_id=chat_id if update.effective_chat.type != ChatType.PRIVATE else None,
                user_id=update.effective_user.id
            )

            # 训练模型
            self.classifier.train(text, is_spam=True)
            self.classifier.save_model()

            await update.message.reply_text(
                "✅ 垃圾消息已投喂成功！\n"
                "📚 模型已更新，所有群组都将受益。\n"
                "感谢你的贡献！"
            )
            logger.info(f"用户 {update.effective_user.id} 投喂了垃圾消息训练数据")

        except Exception as e:
            logger.error(f"投喂训练数据时出错: {e}")
            await update.message.reply_text(f"❌ 投喂失败: {str(e)}")

    async def cmd_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """/stats 命令 - 查看统计信息"""
        from models import count_training_data

        # 获取模型统计
        model_stats = self.classifier.get_stats()

        # 获取数据库统计
        spam_count = count_training_data(is_spam=True)
        ham_count = count_training_data(is_spam=False)

        text = f"""
📊 <b>机器人统计信息</b>

<b>🤖 模型状态:</b>
• 垃圾消息样本: {model_stats['spam_count']}
• 正常消息样本: {model_stats['ham_count']}
• 总训练样本: {model_stats['total_count']}
• 词汇表大小: {model_stats['vocab_size']}

<b>📚 训练数据:</b>
• 垃圾消息记录: {spam_count}
• 正常消息记录: {ham_count}

<b>⚙️ 当前设置:</b>
• 垃圾判定阈值: {settings.spam_threshold * 100}%
• 最大违规次数: {settings.max_violations}

<i>模型会随着训练数据的增加而不断优化</i>
        """
        await update.message.reply_text(text, parse_mode='HTML')

    async def cmd_unban(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """/unban 命令 - 解封用户"""
        if not await self._is_admin(update, context):
            await update.message.reply_text("❌ 只有管理员可以使用此命令")
            return

        chat_id = update.effective_chat.id

        # 检查是否是回复消息
        if update.message.reply_to_message:
            user_id = update.message.reply_to_message.from_user.id
        elif context.args:
            try:
                user_id = int(context.args[0])
            except ValueError:
                await update.message.reply_text("❌ 用户ID必须是数字")
                return
        else:
            await update.message.reply_text(
                "使用方法:\n"
                "1. 回复被封禁用户的消息: /unban\n"
                "2. 提供用户ID: /unban 123456789"
            )
            return

        try:
            # 解除封禁
            await context.bot.unban_chat_member(chat_id=chat_id, user_id=user_id)

            # 更新数据库
            if unban_user(user_id, chat_id):
                await update.message.reply_text(f"✅ 用户 {user_id} 已被解封")
                logger.info(f"管理员 {update.effective_user.id} 解封了用户 {user_id}")
            else:
                await update.message.reply_text(f"⚠️ 用户 {user_id} 不在封禁列表中")

        except Exception as e:
            logger.error(f"解封用户时出错: {e}")
            await update.message.reply_text(f"❌ 解封失败: {str(e)}")

    async def handle_group_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理群组消息"""
        if not update.message or not update.message.text:
            return

        message = update.message
        chat_id = message.chat_id
        user_id = message.from_user.id
        text = message.text

        # 跳过命令和短消息
        if text.startswith('/') or len(text) < 5:
            return

        # 获取或创建设置
        group_settings = get_or_create_group_settings(chat_id, message.chat.title)
        if not group_settings.is_active:
            return

        # 预测
        is_spam, confidence = self.classifier.predict(text)
        threshold = float(group_settings.spam_threshold or settings.spam_threshold)

        # 记录日志
        logger.debug(f"消息分析: user={user_id}, is_spam={is_spam}, confidence={confidence:.4f}, text={text[:50]}...")

        # 如果置信度超过阈值，处理垃圾消息
        if is_spam and confidence >= threshold:
            await self._handle_spam_message(update, context, text, confidence)

    async def _handle_spam_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE,
                                   text: str, confidence: float):
        """处理检测到的垃圾消息"""
        message = update.message
        chat_id = message.chat_id
        user_id = message.from_user.id
        user = message.from_user

        try:
            # 1. 删除消息
            await message.delete()
            logger.info(f"删除垃圾消息: user={user_id}, confidence={confidence:.4f}")

            # 2. 记录违规
            violation_count = get_user_violation_count(user_id, chat_id)
            add_user_violation(
                user_id=user_id,
                chat_id=chat_id,
                message_text=text[:500],
                confidence=confidence,
                is_banned=False
            )

            # 3. 添加到训练数据（自动标记）
            add_training_data(
                text=text,
                is_spam=True,
                source='auto',
                chat_id=chat_id,
                message_id=message.message_id,
                user_id=user_id
            )

            # 4. 检查是否需要封禁
            if violation_count + 1 >= settings.max_violations:
                # 封禁用户
                await context.bot.ban_chat_member(chat_id=chat_id, user_id=user_id)

                add_banned_user(
                    user_id=user_id,
                    chat_id=chat_id,
                    username=user.username,
                    first_name=user.first_name,
                    reason=f"连续发送垃圾消息 {settings.max_violations} 次",
                    banned_by=None
                )

                # 更新违规记录为已封禁
                add_user_violation(
                    user_id=user_id,
                    chat_id=chat_id,
                    is_banned=True
                )

                logger.warning(f"用户 {user_id} 因连续发送垃圾消息被封禁")

                # 发送通知（可选）
                try:
                    await context.bot.send_message(
                        chat_id=chat_id,
                        text=f"🚫 用户 {user.first_name} 因连续发送垃圾消息已被封禁",
                        parse_mode='HTML'
                    )
                except Exception:
                    pass

        except Exception as e:
            logger.error(f"处理垃圾消息时出错: {e}")

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理回调查询"""
        query = update.callback_query
        await query.answer()

        data = query.data
        chat_id = update.effective_chat.id

        if data.startswith("unban:"):
            # 解封用户
            user_id = int(data.split(":")[1])
            try:
                await context.bot.unban_chat_member(chat_id=chat_id, user_id=user_id)
                unban_user(user_id, chat_id)
                await query.edit_message_text(f"✅ 用户 {user_id} 已被解封")
                logger.info(f"管理员通过按钮解封用户 {user_id}")
            except Exception as e:
                await query.edit_message_text(f"❌ 解封失败: {str(e)}")

        elif data.startswith("markham:"):
            # 标记为正常消息
            data_id = int(data.split(":")[1])
            # 这里可以添加逻辑将训练数据标记为正常
            await query.edit_message_text("✅ 已标记为正常消息（功能开发中）")

    async def _is_admin(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """检查用户是否为管理员"""
        if update.effective_chat.type == ChatType.PRIVATE:
            return True

        user_id = update.effective_user.id
        chat_id = update.effective_chat.id

        try:
            member = await context.bot.get_chat_member(chat_id, user_id)
            return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
        except Exception as e:
            logger.error(f"检查管理员权限时出错: {e}")
            return False

    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """错误处理器"""
        logger.error(f"更新 {update} 导致错误: {context.error}")


async def main():
    """主函数"""
    bot = SpamBot()
    await bot.start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("机器人已停止")
    except Exception as e:
        logger.error(f"运行时错误: {e}")
