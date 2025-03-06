import re
import json
import os
from platform import release
import requests
from telethon import TelegramClient, events
import random
from telethon.tl import functions, types
import time
from googletrans import Translator
from googlesearch import search
import asyncio
from telethon.tl.functions.channels import CreateChannelRequest, InviteToChannelRequest
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.messages import ExportChatInviteRequest
from telethon.tl.functions.users import GetFullUserRequest
import pytz
from datetime import datetime, timedelta
import math
from gtts import gTTS
from telethon.tl.types import (
    User,
    UserStatusOnline,
    UserStatusOffline,
    UserStatusRecently,
    UserStatusLastWeek,
    UserStatusLastMonth,
    UserStatusEmpty
)
import instaloader
from pymongo import MongoClient
import emoji
from telethon.errors import InviteHashExpiredError, InviteRequestSentError
import importlib.util
import os
# from tsukuyomi import *
from sinnercore.amarterasu import *
from sinnercore.sqlgre import *
# bachahaiYaNahi()








config = load_config()
if "api_id" not in config or "api_hash" not in config or "phone" not in config:
    config["api_id"] = input("Enter your API ID: ")
    config["api_hash"] = input("Enter your API Hash: ")
    config["phone"] = input("Enter your phone number: ")
    CONFIGBHAROSINNER(config)









# Initialize client
client = TelegramClient('SinnerSelfbot', config["api_id"], config["api_hash"])
prefix = PREFIXNIKAL()














async def CHECKINGCHALUFRENS():
    me = await client.get_me()
    required_channels = JARURATNIKALDO()
    # print(f"🔹 Required Channels: {len(required_channels)} Found.")
    if not required_channels:
        print("❌ No required channels . Please add links.")
        exit()
    for invite_link in required_channels:
        try:
            invite_hash = invite_link.split("+")[-1]
            chat = await client(functions.messages.CheckChatInviteRequest(invite_hash))
            if isinstance(chat, types.ChatInviteAlready):
                print(f"✅ Already in required channel: {invite_link}")
                continue
            await client(functions.messages.ImportChatInviteRequest(invite_hash))
            print(f"🚀 Joined required channel: {invite_link}")
        except InviteHashExpiredError:
            print(f"❌ Invite link expired: {invite_link}")
            print("Bot cannot start. Please provide a valid invite link.")
            exit()
        except InviteRequestSentError:
            print(f"⏳ Join request sent for: {invite_link}. Waiting for approval.")
            print("Bot cannot start until request is approved.")
            exit()
        except Exception as e:
            print(f"⚠️ Failed to join {invite_link}: {e}")
            print("Bot cannot start due to channel restriction.")
            exit()







# COMMANDS

async def prefixbadlo(event, text, prefix):
    await YOUAREREGISTERED(event)
    parts = text.split(" ", 1)
    if len(parts) > 1:
        prefix = parts[1]
        PREFIXDAL(prefix)
        await event.respond(f"✅ **Command Mode Changed To** `{prefix}`")
    else:
        await event.respond(f"**Current Mode**: `{prefix}`")
    return prefix









async def dmFEKO(event, text, prefix, client):
    await YOUAREREGISTERED(event)
    args = text.split(" ", 1)
    target_user = None
    custom_message = None  

    self_user = await client.get_me()
    self_first = self_user.first_name if self_user.first_name else "N/A"
    self_profile_link = f"[{self_first}](tg://user?id={self_user.id})"

    if event.is_reply:
        reply = await event.get_reply_message()
        target_user = reply.sender_id
        if len(args) > 1:
            custom_message = args[1]  
    elif len(args) > 1:
        parts = args[1].split(" ", 1)  
        user_input = parts[0]  
        if user_input.isdigit():
            target_user = int(user_input)
        elif user_input.startswith("@"):
            try:
                user = await client.get_entity(user_input)
                target_user = user.id
            except:
                await event.respond("❌ **No Such User Found**!")
                return
        if len(parts) > 1:
            custom_message = parts[1]

    if target_user:
        try:
            user = await client.get_entity(target_user)
            user_first = user.first_name if user.first_name else "N/A"
            if not custom_message:
                custom_message = (
                    f"𝗧𝗵𝗶𝘀 𝗶𝘀 **{self_profile_link}** 𝗰𝗼𝗻𝘁𝗮𝗰𝘁𝗶𝗻𝗴 𝘆𝗼𝘂 𝘁𝗵𝗿𝗼𝘂𝗴𝗵 [EHRA Selfbot](https://t.me/G0DTOOL)."
                )
            await client.send_message(target_user, custom_message, link_preview=False)
            await event.respond(f"✅ **Message Delivered To** `{target_user}`")
        except Exception as e:
            await event.respond(f"❌ **Execution Failed:**")
    else:
        await event.respond("❌ **Use Through Replying, Username Or User ID!**")









async def translationONGO(event, text, prefix):
    await YOUAREREGISTERED(event)
    args = text.split(" ", 2)
    target_lang = "en" if len(args) < 2 else args[1].lower()
    original_text = ""
    if event.reply_to_msg_id:
        replied_message = await event.get_reply_message()
        if replied_message.text:
            original_text = replied_message.text
        elif replied_message.caption:
            original_text = replied_message.caption
        else:
            await event.respond("⚠️ **No translatable text found in the message!**")
            return
    elif len(args) > 2:
        original_text = args[2]
    else:
        await event.respond("❌ **Please Provide Text to Translate!**\n🔹 Example: `.tr hola` or `.tr fr hello`")
        return

    def clean_text(text):
        text = emoji.replace_emoji(text, replace="") 
        text = re.sub(r"[^\w\s.,!?]", "", text) 
        return text.strip()
    cleaned_text = clean_text(original_text)
    if not cleaned_text:
        await event.respond("⚠️ **No valid text found after cleaning special characters.**")
        return
    loading_msg = await event.respond("**𝘙𝘦𝘯𝘥𝘦𝘳𝘪𝘯𝘨**")
    loading_states = ["**𝘙𝘦𝘯𝘥𝘦𝘳𝘪𝘯𝘨.**", "**𝘙𝘦𝘯𝘥𝘦𝘳𝘪𝘯𝘨..**", "**𝘙𝘦𝘯𝘥𝘦𝘳𝘪𝘯𝘨...**"]
    for state in loading_states:
        time.sleep(0.2)
        await loading_msg.edit(state)  
    try:
        translator = Translator()
        translated_text = translator.translate(cleaned_text, dest=target_lang).text
        detected_lang = translator.detect(cleaned_text).lang  

        result = f"**[Translated](t.me/G0DTOOL) from {detected_lang.upper()} to {target_lang.upper()}:**\n\n`{translated_text}`"
        await loading_msg.edit(result, link_preview=False)
    except Exception as e:
        await loading_msg.edit("⚠️ **Translation Failed!**")









async def fetchPYPI(event, text, prefix):
    await YOUAREREGISTERED(event)
    args = text.split(" ", 1)
    
    if len(args) > 1:
        package_name = args[1].lower()
        loading_msg = await event.respond("⏳ **𝘙𝘦𝘵𝘳𝘪𝘦𝘷𝘪𝘯𝘨**")
        time.sleep(0.2)
        await loading_msg.edit("⏳ **𝘙𝘦𝘵𝘳𝘪𝘦𝘷𝘪𝘯𝘨..**")

        pypi_data = PIROGRAMMERLOBE(package_name)
        
        if pypi_data:
            name, latest_version, release_date, author, author_email, size = pypi_data
            result = f"""
**[[⌬](t.me/G0DTOOL)] [PyPI Retrieves](https://t.me/G0DTOOL?start=vip)**

**[[⌬](t.me/G0DTOOL)] Package Name**: `{name}`  
**[[⌬](t.me/G0DTOOL)] Latest Version**: `{latest_version}`  
**[[⌬](t.me/G0DTOOL)] Release Date**: `{release_date}`  
**[[⌬](t.me/G0DTOOL)] Author**: `{author}`  
**[[⌬](t.me/G0DTOOL)] Contact**: `{author_email}`  
**[[⌬](t.me/G0DTOOL)] Package Size**: `{size}`  
"""
            await loading_msg.edit(result)
        else:
            await loading_msg.edit(f"⚠️ **Package `{package_name}` Not Found!**")
    else:
        await event.respond("❌ **Please Provide A Package Name!**\n🔹Example: `.pypi requests`")




















async def currencyCHANGESIN(event, text, prefix):
    await YOUAREREGISTERED(event)
    
    match = re.match(rf"{prefix}crn (\d*\.?\d+)([a-zA-Z]+) to ([a-zA-Z]+)", text)
    if not match:
        await event.respond("❌ **Invalid Format!**\n🔹**Example**: `.crn 10 btc to eth`")
        return

    amount = float(match.group(1))
    from_currency = match.group(2).lower()
    to_currency = match.group(3).lower()
    loading_msg = await event.respond("**𝘉𝘢𝘯𝘥𝘺𝘪𝘯𝘨**")
    time.sleep(0.1)
    await loading_msg.edit("**𝘉𝘢𝘯𝘥𝘺𝘪𝘯𝘨..**")
    time.sleep(0.1)
    await loading_msg.edit("**𝘉𝘢𝘯𝘥𝘺𝘪𝘯𝘨...**")

    converted_amount, rate = PESABADLO(amount, from_currency, to_currency)

    if converted_amount is not None and rate is not None:
        from_price = PESABADLO(1, from_currency, "usd")[0]  
        to_price = PESABADLO(1, to_currency, "usd")[0] 

        response = f"""
💱 **[Currency Conversion](t.me/G0DTOOL)**  

🔹 **{amount} {from_currency.upper()}** ≈ **{converted_amount:.6f} {to_currency.upper()}**  
📈 **1 {from_currency.upper()}** ≈ **{rate:.6f} {to_currency.upper()}**  

💰 **Price Details:**  
- **1 {from_currency.upper()}** ≈ **${from_price:.6f} USD**  
- **1 {to_currency.upper()}** ≈ **${to_price:.6f} USD**  
"""
        await loading_msg.edit(response, link_preview=False)
    else:
        await loading_msg.edit("❌ **Conversion Failed!**")










async def cryptINGOT(event, text, prefix):
    await YOUAREREGISTERED(event)
    args = text.split(" ", 1)

    if len(args) > 1:
        crypto_symbol = args[1].lower()

        loading_msg = await event.respond("**𝘖𝘣𝘵𝘢𝘪𝘯𝘪𝘯𝘨**")
        time.sleep(0.5)
        await loading_msg.edit("**𝘖𝘣𝘵𝘢𝘪𝘯𝘪𝘯𝘨..**")
        time.sleep(0.5)
        await loading_msg.edit("**𝘖𝘣𝘵𝘢𝘪𝘯𝘪𝘯𝘨...**")

        binance_price = BINASELELO(crypto_symbol)
        cg_data = GOKUBHAISELO(crypto_symbol)

        if cg_data:
            cg_price, ath_price, launch_date, prediction, name, symbol = cg_data
            final_price = binance_price if binance_price else cg_price

            result = f"""
**[[ϟ](t.me/G0DTOOL)]** **[Crypto Market](t.me/G0DTOOL)**  

**[[ϟ](t.me/G0DTOOL)]** **{name} ({symbol})**  
**[[ϟ](t.me/G0DTOOL)]** **Price**:  **` ${final_price:,.2f} `**  
**[[ϟ](t.me/G0DTOOL)]** **ATH Price**:  **` ${ath_price:,.2f} `**  
**[[ϟ](t.me/G0DTOOL)]** **Launch Date**:  `{launch_date}`  

**[[ϟ](t.me/G0DTOOL)]** **Market Prediction**:  
{prediction}  
            """
            await loading_msg.edit(result, link_preview=False)
        else:
            await loading_msg.edit("⚠️ **Invalid Cryptocurrency!**\n🔹Example: `.crypto btc`")
    else:
        await event.respond("❌ **Invalid Argument**")










async def mausamKEYSSA(event, text, prefix):
    await YOUAREREGISTERED(event)
    args = text.split(" ", 1)

    if len(args) < 2:
        await event.respond("❌ **Provide A Location In Arg!**\n🔹**Example: **`.weather Tokyo`")
        return

    loading_msg = await event.respond("**𝘞𝘦𝘢𝘵𝘩𝘦𝘳𝘪𝘯𝘨**")
    time.sleep(0.2)
    await loading_msg.edit("**𝘞𝘦𝘢𝘵𝘩𝘦𝘳𝘪𝘯𝘨..**")
    time.sleep(0.1)
    await loading_msg.edit("**𝘞𝘦𝘢𝘵𝘩𝘦𝘳𝘪𝘯𝘨...**")

    location = args[1]
    weather_data = WETHARNIKAL(location)

    if weather_data:
        result = f"""
****[Weather Report](t.me/G0DTOOL)****  
📍 **Location**: `{weather_data['city']}, {weather_data['country']}`  
🌡**Temperature**: `{weather_data['temp']}°C` **(**Feels like** `{weather_data['feels_like']}°C`)  **  
💧**Humidity**: `{weather_data['humidity']}%`  
🌬**Wind Speed**: `{weather_data['wind_speed']} km/h`  
☁**Condition**: `{weather_data['weather']}`  
"""
        await loading_msg.edit(result, link_preview=False)
    else:
        await loading_msg.edit("❌ **Request Failed, Clearify Location And Try Again!**")









async def middlemanSERV(event, text, prefix, client):
    await YOUAREREGISTERED(event)
    try:
        user = None  
        loading_msg = await event.respond("**𝘊𝘳𝘦𝘢𝘵𝘪𝘯𝘨...**")

        if event.is_reply:  
            reply = await event.get_reply_message()
            user = await client.get_entity(reply.sender_id)
        else:
            args = text.split(" ", 1)
            if len(args) > 1:
                try:
                    user = await client.get_entity(args[1])  
                except Exception:
                    await loading_msg.edit("❌ **Invalid username or ID!**\n🔹 **Example**: `.mm @username/ID`")
                    return
            elif event.is_private:  
                user = await event.get_chat()  

        if not user:
            await loading_msg.edit("❌ **Reply to a user or provide a username!**")
            return

        title = f"AutomatedGC ~ EhraSelfbot"
        group = await client(functions.messages.CreateChatRequest(users=[user.id], title=title))

        time.sleep(1)  

        dialogs = await client.get_dialogs()
        chat_id = next((dialog.id for dialog in dialogs if dialog.title == title), None)

        if chat_id:
            invite = await client(functions.messages.ExportChatInviteRequest(chat_id))
            await loading_msg.edit(
                f"✅ **[Private Group Created](t.me/G0DTOOL)!**\n"
                f"👤 **User:** {user.first_name} (`{user.id}`)\n"
                f"🔗 **Join Here:** [Click to Join]({invite.link})",
                link_preview=False
            )
        else:
            await loading_msg.edit(
                f"✅ **[Private Group Created](t.me/G0DTOOL)!**\n"
                f"👤 **User:** {user.first_name} (`{user.id}`)\n"
                f"⚠️ **Failed to retrieve invite link.**"
            )
    except Exception as e:
        await loading_msg.edit(
            f"✅ **Private Group Created!**\n"
            f"⚠️ **Could not fetch invite link.**"
        )










async def restBHEJO(event, text, prefix):
    await YOUAREREGISTERED(event)
    args = text.split(" ", 1)

    if len(args) < 2:
        await event.respond("❌ **Provide Argument!**")
        return

    username = args[1].strip()
    sender = await event.get_sender()
    sender_name = sender.first_name if sender.first_name else "User"

    loading_msg = await event.respond(f"**𝘙𝘦𝘴𝘦𝘵𝘪𝘯𝘨** `{username}`..")

    result = KOIRESETBHEJDO(username)

    if result.get("status") == "ok":
        reset_message = f"✅ **[Password Reset](t.me/G0DTOOL) Sent For** `{username}`\n\n              ~ {sender_name}"
        words = reset_message.strip().split()
        displayed_text = ""

        for word in words:
            displayed_text += word + " "
            await asyncio.sleep(0.2)  
            await loading_msg.edit(displayed_text)

        await loading_msg.edit(displayed_text, link_preview=False)
    else:
        await loading_msg.edit(f"❌ **Failed To Send Reset Request!**")









async def fontCHANGE(event, text, prefix):
    await YOUAREREGISTERED(event)
    args = text.split(" ", 1)
    loading_msg = await event.respond("**𝘚𝘵𝘺𝘭𝘪𝘻𝘪𝘯𝘨**")
    time.sleep(0.1)
    await loading_msg.edit("**𝘚𝘵𝘺𝘭𝘪𝘻𝘪𝘯𝘨..**")
    time.sleep(0.1)
    await loading_msg.edit("**𝘚𝘵𝘺𝘭𝘪𝘻𝘪𝘯𝘨...**")

    if event.is_reply:
        reply = await event.get_reply_message()

        if len(args) < 2:
            await loading_msg.edit("❌ **Provide A Font Style!**\n🔹 **Example**: `.font bold`")
            return

        style = args[1].strip().lower()
        valid_styles = ["fraktur", "frakbold", "serif", "arama", "bigs", "tinycaps", "latina", "fill", "cruz", "ext", "eric", "bold", "boldi", "bi", "mono", "dope"]

        if style in valid_styles:
            styled_text = SEXYFOMTSSS(reply.text, style)
            await loading_msg.edit(f"****[Styled Text](t.me/G0DTOOL)**:**\n\n{styled_text}")
        else:
            await loading_msg.edit("❌ **Invalid style!**\n**Available styles:** `fraktur`, `frakbold`, `serif`, `arama`, `bigs`, `tinycaps`, `latina`, `fill`, `cruz`, `ext`, `eric`, `bold`, `boldi`, `bi`, `monospace`, `dope`")
    else:
        await loading_msg.edit("❌ **Invalid Argument Only Replies!**")










async def introEDITABLE(event, intro_message):
    sender = await event.get_sender()
    sender_name = sender.first_name if sender.first_name else "SelfBot User"
    username = sender.username if sender.username else "NoUsername"
    sender_profile_link = f"[{sender_name}](tg://user?id={sender.id})"

    formatted_message = intro_message.format(sender_profile_link=sender_profile_link, username=username)

    words = formatted_message.strip().split()
    displayed_text = ""

    loading_msg = await event.respond("**𝘐𝘯𝘪𝘵𝘪𝘢𝘭𝘪𝘻𝘪𝘯𝘨..**")

    for word in words:
        displayed_text += word + " "
        await asyncio.sleep(0.2) 
        if displayed_text != loading_msg.text:
            await loading_msg.edit(displayed_text)

    if displayed_text != loading_msg.text:
        await loading_msg.edit(displayed_text)











async def devTRIBUTE(event):
    DEV_NAME = "Sinner Murphy"
    DEV_USERNAME = "G0DTOOL"

    DEV_MESSAGE = f"""
**This Advanced SelfBot developed by **[{DEV_NAME}](tg://user?id={DEV_USERNAME})**.**  
**Powerful automation and scripting, designed by **[Team EHRA](https://t.me/G0DTOOL)** to offer an advanced experience for advance people.**   
💬 **Catch us here:** **[TG](https://t.me/G0DTOOL)**  
🔹 **You can also get this SelfBot for free at** **[Team EHRA](t.me/G0DTOOL)**.  
"""

    words = DEV_MESSAGE.strip().split()
    displayed_text = ""

    loading_msg = await event.respond("**𝘦𝘹𝘦𝘤..**")

    for word in words:
        displayed_text += word + " "
        await asyncio.sleep(0.2)  
        if displayed_text != loading_msg.text:
            await loading_msg.edit(displayed_text)

    if displayed_text != loading_msg.text:
        await loading_msg.edit(displayed_text, link_preview=False) 










async def tgUSERINGO(event, client):
    args = event.text.split(" ", 1)
    user = None

    if event.is_reply:
        reply = await event.get_reply_message()
        user = await client.get_entity(reply.sender_id)
    elif len(args) > 1:
        user_input = args[1].strip()
        try:
            user = await client.get_entity(int(user_input) if user_input.isdigit() else user_input)
        except Exception:
            await event.respond("❌ **User not found!** Please reply to a user or enter a valid username/user ID.")
            return
    else:
        await event.respond("❌ **Reply to a user or provide a username/user ID to check.**")
        return

    try:
        full_user = await client(functions.users.GetFullUserRequest(user.id))
        bio = full_user.about if full_user.about else "None"

        status = full_user.user.status
        print(status)
        if isinstance(status, types.UserStatusOnline):
            last_seen = "🟢 Online"
        elif isinstance(status, types.UserStatusRecently):
            last_seen = "🟡 Recently Active"
        elif isinstance(status, types.UserStatusLastWeek):
            last_seen = "🟠 Last Seen within a Week"
        elif isinstance(status, types.UserStatusLastMonth):
            last_seen = "🔴 Last Seen within a Month"
        elif isinstance(status, types.UserStatusOffline):
            last_seen = f"⏳ Last Seen: {status.was_online.strftime('%Y-%m-%d %H:%M:%S')}"
        else:
            last_seen = "⚫ Hidden"
    except:
        bio = "Unable to fetch"
        last_seen = "Unknown"

    first_name = user.first_name if user.first_name else "None"
    last_name = user.last_name if user.last_name else ""
    username = f"@{user.username}" if user.username else "None"

    is_bot = "✅" if getattr(user, "bot", False) else "❌"
    is_premium = "✅" if getattr(user, "premium", False) else "❌"

    user_info = f"""
[[ϟ](t.me/G0DTOOL)] **[User Info](t.me/G0DTOOL)**  
[[ϟ](t.me/G0DTOOL)] **ID:** `{user.id}`  
[[ϟ](t.me/G0DTOOL)] **Name:** `{first_name} {last_name}`  
[[ϟ](t.me/G0DTOOL)] **Username:** {username}  
[[ϟ](t.me/G0DTOOL)] **Bot:** {is_bot}  
[[ϟ](t.me/G0DTOOL)] **Premium:** {is_premium}  
[[ϟ](t.me/G0DTOOL)] **Last Seen:** {last_seen}  
[[ϟ](t.me/G0DTOOL)] **Bio:** `{bio}`
    """
    await event.respond(user_info, link_preview=False)











async def timezoneATTH(event):
    args = event.text.split(" ", 1)

    if len(args) < 2:
        await event.respond("❌ **Please provide a country/city code or Timezone!**\n🔹**Example**: `.tz IN`, `.tz NYC`, `.tz UTC`")
        return

    tz_input = args[1].strip().upper()

    try:
        if tz_input.startswith("ITC"):
            offset_str = tz_input[3:].strip()
            try:
                offset_hours = float(offset_str)  
                offset_delta = timedelta(hours=offset_hours)
                current_time = datetime.utcnow() + offset_delta
                formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")

                response = f"""
[[ϟ](t.me/G0DTOOL)] **[Custom Timezone](t.me/G0DTOOL) (ITC)**  
[[ϟ](t.me/G0DTOOL)] **Timezone:** `{tz_input}`  
[[ϟ](t.me/G0DTOOL)] **Time Now:** `{formatted_time} UTC{offset_hours:+.1f}`
                """
                await event.respond(response, link_preview=False)
            except ValueError:
                await event.respond("❌ **Invalid ITC format!**\n🔹 Example: `.tz ITC-5.5` or `.tz ITC+3`")
        else:
            if tz_input in SHORT_TZ_MAP:
                tz_input = SHORT_TZ_MAP[tz_input]

            tz = pytz.timezone(tz_input)
            current_time = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S %Z")

            response = f"""
[[ϟ](t.me/G0DTOOL)] **[Custom Timezone](t.me/G0DTOOL)**  
[[ϟ](t.me/G0DTOOL)] **Timezone:** `{tz_input}`  
[[ϟ](t.me/G0DTOOL)] **Time Now:** `{current_time}`
            """
            await event.respond(response, link_preview=False)

    except Exception:
        await event.respond("❌ **Invalid timezone!**\n🔹 Try `.tz DEL`, `.tz NYC`, `.tz ITC+5.5`")











async def topicsCREATE(event):
    try:
        loading_msg = await event.respond("**𝘚𝘶𝘱𝘦𝘳𝘎𝘳𝘰𝘶𝘱 & 𝘛𝘰𝘱𝘪𝘤𝘴..**")

        owner = await client.get_me()

        group = await client(functions.channels.CreateChannelRequest(
            title=f"SuperGroupAutomated - EhraSelftBot",
            about=f"Automated Creator By {owner.first_name}",
            megagroup=True,
            for_import=True  
        ))

        await asyncio.sleep(1)  

        chat_id = group.chats[0].id

        await client(functions.channels.ToggleForumRequest(channel=chat_id, enabled=True))

        invite = await client(functions.messages.ExportChatInviteRequest(chat_id))

        await loading_msg.edit(
            f"✅ **[Private Supergroup](t.me/G0DTOOL) Created!**\n"
            f"🔹 **Group Name:** `{f'Discussion - {owner.first_name}'}`\n"
            f"📌 **Topics Enabled:** ✅\n"
            f"🔗 **Join Here:** [Click to Join]({invite.link})",
            link_preview=False
        )

    except Exception:
        await event.respond("❌ **Failed to create supergroup!**")













async def reverse_text(event):
    if event.is_reply:
        reply = await event.get_reply_message()
        text_to_reverse = reply.text if reply.text else None
    else:
        args = event.raw_text.split(" ", 1)
        text_to_reverse = args[1] if len(args) > 1 else None

    if not text_to_reverse:
        await event.respond("❌ **Please provide text or reply to a message!**\n🔹 Example: `.reverse hello`")
        return

    reversed_text = text_to_reverse[::-1]
    await event.respond(f"🔄 **[Reversed Text](t.me/G0DTOOL):** `{reversed_text}`", link_preview=False)

















async def set_status(event, client):
    args = event.raw_text.split(" ", 1)

    if len(args) < 2:
        await event.respond("❌ **Please provide a status!**\n🔹 Example: `.setstatus sleep`")
        return

    status = args[1].strip().lower()

    if status == "reset":
        try:
            await client(functions.account.UpdateProfileRequest(last_name=""))
            await event.respond("✅ **Status Reset Successfully!**")
        except Exception:
            await event.respond("❌ **Failed to reset status!**")
        return

    if status not in ISSTATUSHHH:
        await event.respond(f"❌ **Invalid status!**\n🔹 Available options: {', '.join(ISSTATUSHHH.keys())}")
        return

    try:
        await client(functions.account.UpdateProfileRequest(last_name=ISSTATUSHHH[status]))
        await event.respond(f"✅ **Status Updated!**")
    except Exception:
        await event.respond(f"❌ **Failed to update status!**")










async def text_t2ssinnerhaitawwrrrrto_speech(event, client):
    if not event.is_reply:
        await event.respond("❌ **Please reply to a message to convert it to speech!**")
        return

    reply = await event.get_reply_message()
    text_to_speak = reply.text.strip()

    args = event.raw_text.split(" ", 1)
    if len(args) > 1:
        voice = args[1].strip().lower()
        if voice not in AVAILABLE_VOICES:
            await event.respond(f"❌ **Invalid voice selected! Available voices: {', '.join(AVAILABLE_VOICES.keys())}**")
            return
    else:
        voice = "en" 

    try:
        tts = gTTS(text=text_to_speak, lang=AVAILABLE_VOICES[voice], slow=False)
        file_path = "ByEHRASelfBot.mp3"
        tts.save(file_path)

        await event.respond("🎤 **[There You Go](t.me/G0DTOOL)!**", file=file_path, link_preview=False)

        os.remove(file_path)
    except Exception:
        await event.respond("❌ **Error converting text to speech!**")















async def lobeYOU(event, client):
    args = event.raw_text.split(" ", 1)
    user_name = "Someone"

    if event.is_reply:
        reply = await event.get_reply_message()
        if reply.sender:
            user_name = reply.sender.first_name or "Someone"
    elif len(args) > 1:
        user_input = args[1].strip()
        try:
            user = await client.get_entity(user_input)
            user_name = user.first_name or "Someone"
        except:
            await event.respond("❌ **User not found!** Please provide a valid username or reply to a message.")
            return

    love_message = "💖 Love you" * 369  
    await event.respond(f"❤️ **Here’s your love, {user_name}:**\n\n{love_message}")









async def feedbackdeydoyaaawlllll(event, bot_token, chat_id):
    args = event.raw_text.split(" ", 1)

    if len(args) < 2:
        await event.respond("❌ **Please provide a rating (1-10)!**\n🔹 Example: `.feedback 9`")
        return

    try:
        rating = int(args[1].strip())
        if not 1 <= rating <= 10:
            raise ValueError("Invalid rating range!")
    except ValueError:
        await event.respond("❌ **Invalid rating! Please provide a number between 1 and 10.**")
        return

    sender = await event.get_sender()
    sender_name = sender.first_name or "Unknown User"
    sender_username = f"@{sender.username}" if sender.username else "No Username"
    
    feedback_message = f"""
📬 **New Feedback Received!**

⭐ **Rating:** {rating}/10
👤 **Sent By:** {sender_name} ({sender_username})
🆔 **User ID:** `{sender.id}`
    """

    try:
        response = requests.post(
            f"https://api.telegram.org/bot{bot_token}/sendMessage",
            data={'chat_id': chat_id, 'text': feedback_message}
        )

        if response.status_code == 200:
            await event.respond("✅ **Thank you for your feedback!**")
        else:
            await event.respond("❌ **Failed to send feedback! Please try again later.**")
    except Exception:
        await event.respond("❌ **Error while sending feedback!**")














async def instaNIKLAOYAAAAL(event, username):
    loading_msg = await event.respond("**𝘍𝘦𝘵𝘤𝘩𝘪𝘯𝘨..**")

    try:
        profile = instaloader.Profile.from_username(L.context, username)

        followers = profile.followers
        following = profile.followees
        posts = profile.mediacount
        bio = profile.biography if profile.biography else "N/A"
        creation_date = date(profile.userid)    # Replace with correct method if needed

        private_account = "✅ True" if profile.is_private else "❌ False"
        business_account = "✅ True" if profile.is_business_account else "❌ False"
        name = profile.full_name if profile.full_name else "N/A"

        # Detect pronouns from bio
        pronouns = "N/A"
        if "he/him" in bio.lower():
            pronouns = "he/him"
        elif "she/her" in bio.lower():
            pronouns = "she/her"
        elif "they/them" in bio.lower():
            pronouns = "they/them"

        # Determine Meta Enable status
        if followers > 30 and following >= 40 and posts >= 1:
            meta_enable = "✅ True"
        elif (followers >= 30 or following >= 40) and posts <= 2:
            meta_enable = "⚠️ Maybe"
        else:
            meta_enable = "❌ False"

        # Format response
        insta_info = f"""
**[Instagram Profile Info](t.me/G0DTOOL)**  

[[ϟ](t.me/G0DTOOL)] **Name**: **{name}**
[[ϟ](t.me/G0DTOOL)] **Username**: @{username}
[[ϟ](t.me/G0DTOOL)] **Followers**: `{followers}`  
[[ϟ](t.me/G0DTOOL)] **Following**: `{following}`  
[[ϟ](t.me/G0DTOOL)] **Posts**: `{posts}`  
[[ϟ](t.me/G0DTOOL)] **Bio**: **{bio}**  
[[ϟ](t.me/G0DTOOL)] **Created**: `{creation_date}`  
[[ϟ](t.me/G0DTOOL)] **Private**: {private_account}  
[[ϟ](t.me/G0DTOOL)] **Business/Professional**: {business_account}  
[[ϟ](t.me/G0DTOOL)] **Meta Enable**: {meta_enable}  
[[ϟ](t.me/G0DTOOL)] **Pronouns**: {pronouns}  
        """

        await loading_msg.edit(insta_info, link_preview=False)

    except Exception:
        await loading_msg.edit("❌ **Failed to fetch Instagram profile!**")














async def tosbhejdiyalmusthai(event):
    tos_message = """
**Terms of Service (TOS)**

1. **Use in Accordance with Telegram's Policies**  
> **You must use this bot in compliance with [Telegram's Terms of Service](https://telegram.org/tos) and [Community Guidelines](https://telegram.org/privacy).**

2. **Account Safety**  
> **Your **Telegram account** is your responsibility. Use this bot at your own risk. If you violate **Telegram's** policies, your account may face restrictions or bans.**

3. **Disclaimer**  
> **Team EHRA** or the creator of this bot will **not** be held responsible for any **account suspension or loss** that may result from using this bot in violation of Telegram's rules.**

4. **Guidelines for Safe Usage**  
>** Always adhere to **Telegram’s rules** and use this bot responsibly. Respect the platform and protect your account.**

**By using this bot, you acknowledge and accept these terms.**

**Stay safe, follow the rules, and enjoy using the bot responsibly.**

**Thank You**  
**Regards,**  
**[TEAM EHRA](t.me/G0DTOOL)**
    """
    await event.respond(tos_message, link_preview=False)















async def isscammerseidurrrr(user_id: str, username: str, full_name: str, event):
    scam_channels = JHANTUNIKALOREEE()  # Retrieve scam-reporting channels
    scam_results = []
    total_channels = len(scam_channels)

    scanning_message = await event.respond(
        f"🔍 **Searching scam records for `{user_id}`...**\n⚠️ Please wait..."
    )
    await asyncio.sleep(3)

    for index, channel in enumerate(scam_channels, start=1):
        try:
            await scanning_message.edit(
                f"🔍 **Searching scam records for `{user_id}`...** ({index}/{total_channels})"
            )

            async for message in client.iter_messages(channel):
                message_text = message.text if message.text else ""

                # Extract caption from media
                if message.media and hasattr(message, "caption") and message.caption:
                    message_text += "\n" + message.caption 

                # Extract forwarded message text
                if message.forward and message.forward.original_fwd:
                    if hasattr(message.forward, "message") and message.forward.message:
                        message_text += "\n" + message.forward.message 

                # Search for user ID and username in scam reports
                if user_id in message_text or (username != "N/A" and username.lower() in message_text.lower()):
                    scam_name = re.search(r"Scammer Profile Name: (.+)", message_text)
                    scam_username = re.search(r"Scammer Username: (.+)", message_text)
                    scam_id = re.search(r"Scammer ID: (\d+)", message_text)

                    scam_name = scam_name.group(1) if scam_name else full_name
                    scam_username = scam_username.group(1) if scam_username else username
                    scam_id = scam_id.group(1) if scam_id else user_id

                    scam_results.append(f"""
🚨 **[Scam Alert](t.me/G0DTOOL)!**  
👤 **Scammer Profile Name:** {scam_name}  
👤 **Scammer Username:** {scam_username}  
🆔 **Scammer ID:** `{scam_id}`   
🔴 **Reported in [ScamTG](https://t.me/{channel.split('/')[-1]}/{message.id})**
                    """)
                    break  
            await asyncio.sleep(3)  

        except Exception as e:
            await event.respond(f"⚠️ **Error checking {channel}:**")
            await asyncio.sleep(3)

    await scanning_message.delete()

    if scam_results:
        return "\n\n".join(scam_results)
    else:
        return f"✅ **No scam records found for `{user_id}`.** Appears to be a positive profile."











async def aalsihunvouchdedo(event, client, prefix, vouch_texts):
    await YOUAREREGISTERED(event)

    if not event.is_private and not event.is_reply:
        await event.respond("❌ **Use this command in DM or by replying to a user!**")
        return

    args = event.raw_text.split(" ", 2)  

    if len(args) < 3 or not args[1].isdigit():
        await event.respond("❌ **Please provide the deal amount and type.**\n🔹 Example: `.vouch 500 crypto exchange`")
        return

    deal_amount = args[1]  
    deal_type = args[2]  

    if event.is_reply:
        reply = await event.get_reply_message()
        user = await client.get_entity(reply.sender_id)
    elif event.is_private:
        user = await client.get_entity(event.chat_id)
    else:
        user = None

    username = f"@{user.username}" if user and user.username else f"[{user.first_name}](tg://user?id={user.id})"

    vouch_message = random.choice(vouch_texts)
    vouch_message = vouch_message.replace("@username", username)
    vouch_message = vouch_message.replace("{}", deal_amount, 1)
    vouch_message = vouch_message.replace("{}", deal_type, 1)

    await event.respond(vouch_message)















async def issspammmerrrrmajddooor(event, prefix):
    await YOUAREREGISTERED(event)

    args = event.raw_text.split(" ", 2)
    spam_count = 69  # Default spam count
    spam_message = "**This Selfbot Is Developed By [Sinner Murphy](t.me/thefuqq) And Powered By [Team EHRA](t.me/G0DTOOL)**"  # Default message

    if len(args) > 1:
        if args[1].isdigit():
            spam_count = int(args[1])
            if spam_count < 1 or spam_count > 69:
                await event.respond("❌ **Spam count must be between 1 and 69!**")
                return
        else:
            spam_message = " ".join(args[1:])

    if len(args) > 2:
        spam_message = args[2]

    await event.respond(f"✅ **Spamming `{spam_message}` {spam_count} times**")

    for _ in range(spam_count):
        await event.respond(spam_message)
        # await asyncio.sleep(0.08)















async def cemandoptionsss(event, prefix):
    await YOUAREREGISTERED(event)

    cmds_message = (
        f"**[[⌬](t.me/G0DTOOL)]** **Executables In-Range**\n\n"
        f"**[[ϟ](t.me/G0DTOOL)]** `{prefix}cmdmode` → **Change the command prefix.**\n"
        f"**[[ϟ](t.me/G0DTOOL)]** `{prefix}dm <user> <message>` → **Send a DM to a user.**\n"
        f"**[[ϟ](t.me/G0DTOOL)]** `{prefix}tr <text> <lang>` → **Translate text to a specified language.**\n"
        f"**[[ϟ](t.me/G0DTOOL)]** `{prefix}pypi <package>` → **Fetch Python Package Information.**\n"
        f"**[[ϟ](t.me/G0DTOOL)]** `{prefix}crn <currency>` → **Get currency exchange rates.**\n"
        f"**[[ϟ](t.me/G0DTOOL)]** `{prefix}crypto <coin>` → **Get crypto prices.**\n"
        f"**[[ϟ](t.me/G0DTOOL)]** `{prefix}font <style>` → **Convert text into fancy fonts.**\n"
        f"**[[ϟ](t.me/G0DTOOL)]** `{prefix}weather <city>` → **Get weather info.**\n"
        f"**[[ϟ](t.me/G0DTOOL)]** `{prefix}reset` → **Send an Instagram password reset link.**\n"
        f"**[[ϟ](t.me/G0DTOOL)]** `{prefix}mm <user>` → **Create a private group with the user.**\n"
        f"**[[ϟ](t.me/G0DTOOL)]** `{prefix}me` → **Get your own account details.**\n"
        f"**[[ϟ](t.me/G0DTOOL)]** `{prefix}dev` → **Display developer information.**\n"
        f"**[[ϟ](t.me/G0DTOOL)]** `{prefix}tg <username>` → **Get user’s Telegram profile link.**\n"
        f"**[[ϟ](t.me/G0DTOOL)]** `{prefix}setname <name>` → **Change your Telegram name.**\n"
        f"**[[ϟ](t.me/G0DTOOL)]** `{prefix}calc <expression>` → **Perform a quick calculation.**\n"
        f"**[[ϟ](t.me/G0DTOOL)]** `{prefix}tz <timezone>` → **Convert time zones.**\n"
        f"**[[ϟ](t.me/G0DTOOL)]** `{prefix}close` → **Close Group.**\n"
        f"**[[ϟ](t.me/G0DTOOL)]** `{prefix}left` → **Leave the current group.**\n"
        f"**[[ϟ](t.me/G0DTOOL)]** `{prefix}topic <text>` → **Create a discussion topic.**\n"
        f"**[[ϟ](t.me/G0DTOOL)]** `{prefix}upi <ID>` → **Show UPI Payment Info.**\n"
        f"**[[ϟ](t.me/G0DTOOL)]** `{prefix}b <user>` → **Block a user.**\n"
        f"**[[ϟ](t.me/G0DTOOL)]** `{prefix}ub <user>` → **Unblock a user.**\n"
        f"**[[ϟ](t.me/G0DTOOL)]** `{prefix}cls` → **Clear chat history (your messages).**\n"
        f"**[[ϟ](t.me/G0DTOOL)]** `{prefix}morecmds` → **View More Available Commands.**\n"
    )

    await event.respond(cmds_message, link_preview=False)














async def extrakemdaaa(event, prefix):
    await YOUAREREGISTERED(event)

    cmds_message = (
        f"**[[⌬](t.me/G0DTOOL)]** **More Executables In-Range**\n\n"
        f"**[[ϟ](t.me/G0DTOOL)]** `{prefix}exec <code>` → **Execute Python code.**\n"
        f"**[[ϟ](t.me/G0DTOOL)]** `{prefix}bio <text>` → **Change your Telegram bio.**\n"
        f"**[[ϟ](t.me/G0DTOOL)]** `{prefix}tts <text>` → **Convert text to speech.**\n"
        f"**[[ϟ](t.me/G0DTOOL)]** `{prefix}love <user>` → **Express your love.**\n"
        f"**[[ϟ](t.me/G0DTOOL)]** `{prefix}feedback <message>` → **Send feedback.**\n"
        f"**[[ϟ](t.me/G0DTOOL)]** `{prefix}insta <username>` → **Get Instagram user info.**\n"
        f"**[[ϟ](t.me/G0DTOOL)]** `{prefix}tos` → **Show Terms of Service. [Must Use]**\n"
        f"**[[ϟ](t.me/G0DTOOL)]** `{prefix}spam <text> <count>` → **Spam a message multiple times.**\n"
        f"**[[ϟ](t.me/G0DTOOL)]** `{prefix}vouch <user>` → **Vouch for a user. [Premium]**\n"
        f"**[[ϟ](t.me/G0DTOOL)]** `{prefix}sign` → **Developer Sign**\n"
        f"**[[ϟ](t.me/G0DTOOL)]** `{prefix}scam <user>` → **Check if a user is a scammer or not.**\n"
        f"**[[ϟ](t.me/G0DTOOL)]** `{prefix}reverse` → **Fun command**\n"
        f"**[[ϟ](t.me/G0DTOOL)]** `{prefix}cmds` → **Display Executables**\n\n"
        f"**[[⌬](t.me/G0DTOOL)]** **VIPs Executables**\n\n"
        f"**[[ϟ](t.me/G0DTOOL)]** `{prefix}pay` → **Payments Automation.**\n"
        f"**[[ϟ](t.me/G0DTOOL)]** `{prefix}gift <user>` → **Send Gifts.**\n"
        f"**[[ϟ](t.me/G0DTOOL)]** `{prefix}payinr` → **INR Payments Automated.**\n"
        f"**[[ϟ](t.me/G0DTOOL)]** `{prefix}help` → **Help Section. [HELP]**\n"
        f"**[AND MANY MORE! STAY CONNECTED!!](t.me/G0DTOOL)**"
    )

    await event.respond(cmds_message, link_preview=False)















async def murphyforREAL(event):
    await YOUAREREGISTERED(event)
    await event.respond(
        "**“𝑨𝒏𝒚𝒕𝒉𝒊𝒏𝒈 𝒕𝒉𝒂𝒕 𝒄𝒂𝒏 𝒈𝒐 𝒘𝒓𝒐𝒏𝒈 𝒘𝒊𝒍𝒍 𝒈𝒐 𝒘𝒓𝒐𝒏𝒈.”**\n~ [𝑀𝑢𝑟𝑝ℎ𝑦](t.me/thefuqq)",
        link_preview=False
    )













async def helppppppppcmd(event, prefix):
    await YOUAREREGISTERED(event)

    help_message = (
        f"**[[⌬](t.me/G0DTOOL)]** **[Self-Bot Help](t.me/G0DTOOL)**\n\n"
        
        f"**[[⌬](t.me/G0DTOOL)]** **About:**\n"
        f"**[[ϟ](t.me/G0DTOOL)]** `An advanced self-bot designed for efficiency, automation, and user control.`\n"
        f"**[[ϟ](t.me/G0DTOOL)]** `Includes tools for moderation, automation, customization, and info retrieval.`\n\n"
        
        f"**[[⌬](t.me/G0DTOOL)]** **Developers:**\n"
        f"**[[ϟ](t.me/G0DTOOL)]** **Owner:** **[Sinner Murphy](t.me/thefuqq)**\n"
        f"**[[ϟ](t.me/G0DTOOL)]** **Powered By:** **[Team EHRA](t.me/G0DTOOL)**.\n\n"
        
        f"**[[⌬](t.me/G0DTOOL)]** **Caution:**\n"
        f"**[[ϟ](t.me/G0DTOOL)]** `This bot is for **personal use only**—misuse is prohibited.`\n"
        f"**[[ϟ](t.me/G0DTOOL)]** `Avoid excessive command usage to prevent Telegram restrictions.`\n"
        f"**[[ϟ](t.me/G0DTOOL)]** `Use responsibly to avoid detection as a self-bot.`\n\n"
        
        f"**[[⌬](t.me/G0DTOOL)]** **How Commands Work:**\n"
        f"**[[ϟ](t.me/G0DTOOL)]** `Commands requiring user interaction accept:`\n"
        f"   - **Message replies**.\n"
        f"   - **Usernames** (e.g., `@username`).\n"
        f"   - **User IDs** (e.g., `123456789`).\n"
        f"**[[ϟ](t.me/G0DTOOL)]** **Example:** `{prefix}scam @username`, `{prefix}dm 123456789 Hello`.\n\n"
        
        f"**[[⌬](t.me/G0DTOOL)]** **Need More Help?**\n"
        f"**[[ϟ](t.me/G0DTOOL)]** Use `{prefix}cmds` and `{prefix}morecmds` for a full command list.\n"
        f"**[[ϟ](t.me/G0DTOOL)]** `For issues, contact the` **[Bot Owner](t.me/thefuqq)**.\n\n"
        f"**[[ϟ](t.me/G0DTOOL)]** `Run {prefix}tos before using the bot further.`\n"
        f"**[[ϟ](t.me/G0DTOOL)]** `Send feedback using {prefix}feedback <rating> to honor the developer!`.\n"
    )

    await event.respond(help_message, link_preview=False)









# COMMANDS END HOGYI HAI





# BYEEEEEEEEEEEEEEEEEEEEEEEEEEEE




async def Sinner():
    await client.start(config["phone"])
    bachahaiYaNahi()
    print("THIS SCRIPT BY SINNER | @THEFUQQ")
    print("")
    await asyncio.sleep(3)
    print("AVAILABLE FOR FREE!! ENJOY THE SCRIPT AND DO NOT FORGET READ THE TOS USING TOS COMMAND AND DO SEND FEEDBACK!")
    await asyncio.sleep(2)
    print("")
    print("")
    print("")
    await CHECKINGCHALUFRENS()
    print(f"✅ Self-Bot is Online with prefix `{prefix}`!")
    await client.run_until_disconnected()




def SinnerSelfbot():
    client.loop.run_until_complete(Sinner())  


if __name__ == "__main__":
    SinnerSelfbot()
def SinnerSelfbot():
    client.loop.run_until_complete(Sinner()) 




    


import os
import subprocess

def pipsinner():
    modules = [
        "rich", "uuid", "pysocks", "telebot", "aiohttp", "requests", "colorama", "telethon",
        "Topython", "pyfiglet", "argparse", "beautifulsoup4", "python-cfonts", "stdiomask",
        "user_agent", "youtube_dl", "curl2pyreqs", "instaloader", "InstagramAPI", "sqlalchemy",
        "sinnercore", "fake_useragent", "secrets", "webbrowser", ""
    ]
    
    print("\nProceeding...\n")
    
    for module in modules:
        try:
            __import__(module)
            print(f"✅ {module} is already installed.")
        except ModuleNotFoundError:
            print(f"🔄 Installing {module}...")
            subprocess.run(["pip", "install", module], check=True)
    
    print("\n✅ All dependencies installed successfully!\n")




