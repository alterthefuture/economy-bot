import re
from pymongo import MongoClient
from discord.ext import commands
from discord.ext import tasks
from helper import *
import discord
import random

cluster = MongoClient("mongo-link")
db = cluster['economy']
collection = db["users"]

intents=discord.Intents.default()
intents.members=True
bot = commands.Bot(command_prefix="!",intents=intents)

@tasks.loop(seconds = 5)
async def add_users():
    await bot.wait_until_ready()
    users = bot.users
    dbusers = []
    for item in collection.find():
      dbusers.append(item["_id"])
    for user in users:
      if user.id not in dbusers:
        collection.insert_one({"_id": user.id, "wallet": 0, "bank": 0, "inventory": []})
        print(f"> {user.id} Has been added to database.")

@bot.event
async def on_ready():
    print("> Bot is online")

    users = bot.users
    dbusers = []
    for item in collection.find():
      dbusers.append(item["_id"])
    for user in users:
      if user.id not in dbusers:
        collection.insert_one({"_id": user.id, "wallet": 0, "bank": 0, "inventory": []})
        print(f"> {user.id} Has been added to database.")

    print("\n> Finished adding servers to database. Bot is ready to go!")

@bot.command()
@commands.cooldown(1, 45, commands.BucketType.user)
async def beg(ctx):
    print(ctx.author.id)
    amount = random.randint(1,350)
    people = ["Rosa Parks", "Donald Trump", "Sonic", "Mario", "Bowser"]

    try:
        get_wallet = collection.find_one({"_id": ctx.author.id})
        collection.update_one({"_id": ctx.author.id}, {"$set": {"wallet": get_wallet["wallet"] + amount}})

        return await ctx.send(embed=correct_embed(f"🎉 Hooray! **{random.choice(people)}** has given you **{amount}** coins."))
    except Exception as error:
        return await ctx.send(embed=error_embed(f"❌ Error has occurred: {error}"))

@bot.command(aliases=['dep'])
@commands.cooldown(1, 5, commands.BucketType.user)
async def deposit(ctx, amount: int):
    get_data = collection.find_one({"_id": ctx.author.id})

    if amount > get_data["wallet"]:
        return await ctx.send(embed=error_embed("❌ You don't have enough wallet for this transaction."))

    try:
        collection.update_one({"_id": ctx.author.id}, {"$set": {"bank": get_data["bank"] + amount}})
        collection.update_one({"_id": ctx.author.id}, {"$set": {"wallet": get_data["wallet"] - amount}})

        bank_amount = collection.find_one({"_id": ctx.author.id})["bank"]

        return await ctx.send(embed=correct_embed(f"✅ **{amount}** coins deposited, current bank balance is **{bank_amount}** coins."))
    except Exception as error:
        return await ctx.send(embed=error_embed(f"❌ Error has occurred: {error}"))

@bot.command(aliases=['wd'])
@commands.cooldown(1, 5, commands.BucketType.user)
async def withdraw(ctx, amount: int):
    get_data = collection.find_one({"_id": ctx.author.id})

    if amount > get_data["bank"]:
        return await ctx.send(embed=error_embed("❌ You don't have enough wallet for this transaction."))

    try:
        collection.update_one({"_id": ctx.author.id}, {"$set": {"bank": get_data["bank"] - amount}})
        collection.update_one({"_id": ctx.author.id}, {"$set": {"wallet": get_data["wallet"] + amount}})

        wallet_amount = collection.find_one({"_id": ctx.author.id})["wallet"]

        return await ctx.send(embed=correct_embed(f"✅ **{amount}** coins withdrawed, current wallet balance is **{wallet_amount}** coins."))
    except Exception as error:
        return await ctx.send(embed=error_embed(f"❌ Error has occurred: {error}"))

@bot.command(aliases=['bal'])
async def balance(ctx):
    get_data = collection.find_one({"_id": ctx.author.id})

    wallet_amount = get_data["wallet"]
    bank_amount = get_data["bank"]

    embed=discord.Embed(title=f"{ctx.author.name}'s Balance",timestamp=ctx.message.created_at,description=f'\n\n**Wallet**: {wallet_amount}\n**Bank**: {bank_amount}',color=discord.Color.green())
    embed.set_footer(text="✨")

    await ctx.send(embed=embed)

@beg.error
async def beg_error(ctx,error):
    if isinstance(error,commands.CommandOnCooldown):
        await ctx.send(embed=error_embed(f"❌ Please wait **{error.retry_after:.2f}** seconds before trying again."))

@withdraw.error
async def withdraw_error(ctx,error):
    if isinstance(error,commands.CommandOnCooldown):
        await ctx.send(embed=error_embed(f"❌ Please wait **{error.retry_after:.2f}** seconds before trying again."))

@deposit.error
async def deposit_error(ctx,error):
    if isinstance(error,commands.CommandOnCooldown):
        await ctx.send(embed=error_embed(f"❌ Please wait **{error.retry_after:.2f}** seconds before trying again."))

add_users.start()
bot.run("token-here")
