import discord

def correct_embed(text):
    embed=discord.Embed(description=text,color=discord.Color.green())

    return embed

def error_embed(text):
    embed=discord.Embed(description=text,color=discord.Color.red())

    return embed