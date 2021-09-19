import os

import discord
from discord.abc import _Overwrites
from dotenv import load_dotenv
from discord.ext import commands
from discord import CategoryChannel

client = commands.Bot(command_prefix="!")

client.list_of_queues = {}
client.count = 1

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

async def createvc(ctx, arg):
    if arg == None:
        await ctx.message.channel.send("Please enter a vc name")
    
    guild = ctx.guild
    category = discord.utils.get(guild.categories, name="Temporary VC")

    if(category == None):
        category = await guild.create_category("Temporary VC", overwrites=None, reason=None)

    channel = await guild.create_voice_channel(arg, overwrites = None, category=category, reason=None)

    return channel

async def deletevc(ctx, vc_name):
    category = discord.utils.get(ctx.guild.categories, name = vc_name)  

    for channel in category.channels:
        if len(channel.members) == 0:
            await channel.delete()

@client.command(name='join', help='get added to queue')
async def join(ctx):
    # check if the channel exists
    voice_state = ctx.author.voice

    if (voice_state == None):
        await ctx.message.channel.send("Please enter a waiting room vc first")
    else:
        voice_channel = voice_state.channel.name

        await ctx.message.channel.send("Name of voice channel: " + voice_channel)

        if voice_channel.lower() in client.list_of_queues:
            client.list_of_queues[voice_channel.lower()].append(ctx.author)
        else:
            new_queue = [ctx.author]
            client.list_of_queues[voice_channel.lower()] = new_queue
        await ctx.message.channel.send("Added " + ctx.author.name + " to queue: " + voice_channel)

@client.command(name='next', help='get next person in specific queue')
@commands.has_role('queue mod')
async def next(ctx, *arg):

    queue_name = ' '.join(arg)
    await ctx.message.channel.send("You entered: " + queue_name)

    if queue_name.lower() in client.list_of_queues:
        await deletevc(ctx, "Temporary VC")

        if len(client.list_of_queues[queue_name.lower()]) != 0:
            user = client.list_of_queues[queue_name.lower()].pop(0)

            await ctx.message.channel.send("You pulled: " + user.name)

            category = discord.utils.get(ctx.guild.categories, name="Temporary VC")

            if ctx.author.voice.channel in category.channels:
                await ctx.message.channel.send("You are in the correct channel")
                voice_channel = ctx.author.voice.channel
                await user.move_to(voice_channel)
            else:
                new_channel = await createvc(ctx, "Temporary")
                await user.move_to(new_channel)
                await ctx.author.move_to(new_channel)
        else:
            await ctx.message.channel.send("Empty queue!")
    else:
        await ctx.message.channel.send("You entered an incorrect vc queue name")

@next.error # <- name of the command + .error
async def next_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send("queue mod role is a requirement to use this command!")

@client.command(name='list', help='get all the people in a specific queue')
async def list(ctx, *arg):

    queue_name = ' '.join(arg)
    await ctx.message.channel.send("You entered: " + queue_name)

    if queue_name.lower() in client.list_of_queues:
        if len(client.list_of_queues[queue_name.lower()]) != 0:
            embed = discord.Embed(title='People in Queue: ' + queue_name)
            namesList = []
            for i in client.list_of_queues[queue_name.lower()]:
                namesList.append(i.name)
            namesList = '\n'.join(namesList)
            embed.add_field(name = str(len(client.list_of_queues[queue_name.lower()])) + " People Remaining", value = namesList)
            await ctx.send(embed=embed)
        else:
            await ctx.message.channel.send("Nobody in this queue")
    else:
        await ctx.message.channel.send("You entered an incorrect vc queue name")

load_dotenv()
client.run(os.getenv('TOKEN'))