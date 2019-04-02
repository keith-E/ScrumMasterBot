import asyncio
import traceback
import logging
from datetime import date, datetime, timedelta

import discord
from discord.ext import commands
import mysql.connector as mysql

TOKEN = 'NTYwMTgyOTQ1NTA0MTY1OTQy.D3wP_A.43NEAeeKNw7BMpWXOh5ivVPhAcA'
client = commands.Bot(command_prefix='!')
DAILY_TIME = 1
SPRINT_TIME = 14
MYSQL_USERNAME = 'keagleson'
MYSQL_HOST = '127.0.0.1'
MYSQL_DB_NAME = 'goals'


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


@client.event
async def on_command_error(error, ctx):

    if isinstance(error, commands.MissingRequiredArgument):
        message = ctx.message
        content = message.content

        if content.startswith('!add-daily') or content.startswith('!add-sprint'):
            await client.send_message(message.channel, 'You must provide a goal description with this command.')
            await client.send_message(message.channel, 'Example: !add_daily Tie my shoes.')


@client.command(pass_context=True, name='add-daily')
async def add_daily(ctx, *daily_description):

    daily_goal = ''

    for word in daily_description:
        daily_goal += word
        daily_goal += ' '

    goal_loop = asyncio.get_event_loop()
    goal_loop.run_until_complete(process_goal(ctx, 'daily', daily_goal, DAILY_TIME))
    goal_loop.close()


@client.command(pass_context=True, name='add-sprint')
async def add_sprint(ctx, *sprint_description):

    sprint_goal = ''

    for word in sprint_description:
        sprint_goal += word
        sprint_goal += ' '

    goal_loop = asyncio.get_event_loop()
    goal_loop.run_until_complete(process_goal(ctx, 'sprint', sprint_goal, SPRINT_TIME))
    goal_loop.close()


async def process_goal(ctx, goal_type, goal_description, time_limit):
    discord_message = ctx.message
    goal_author = str(discord_message.author)

    if goal_type is 'daily':
        add_goal_to_database(goal_type, goal_author, goal_description, 'INCOMPLETE')
    elif goal_type is 'sprint':
        add_goal_to_database(goal_type, goal_author, goal_description, 'INCOMPLETE')

    start_day = datetime.now()
    due_day = datetime.now() + timedelta(time_limit)
    days, hours, minutes, seconds = get_time_left(start_day, due_day)

    msg = (f"{discord_message.author.mention} has added a {goal_type} goal of: {goal_description}. "
           f"This goal is scheduled to complete in: {str(days)} days, {str(hours)} hours, {str(minutes)} "
           f"minutes, and {str(seconds)} seconds.")

    await client.send_message(discord_message.channel, msg)


def add_goal_to_database(table_name, author, description, status):
    # TODO: cut the context off earlier to restrict dependency
    cnx = mysql.connect(user=MYSQL_USERNAME, host=MYSQL_HOST, database=MYSQL_DB_NAME)
    cursor = cnx.cursor()
    start_date = datetime.now().date()

    if table_name is 'daily':
        add_daily = ("INSERT INTO daily "
                     "(author, description, start_date, status) "
                     "VALUES (%s, %s, %s, %s)")

        data_daily = (author, description, start_date, status)
        cursor.execute(add_daily, data_daily)
        cnx.commit()
    elif table_name is 'sprint':
        add_sprint = ("INSERT INTO sprint "
                     "(author, description, start_date, status) "
                     "VALUES (%s, %s, %s, %s)")

        data_sprint = (author, description, start_date, status)
        cursor.execute(add_sprint, data_sprint)
        cnx.commit()

    cursor.close()
    cnx.close()


def get_time_left(start_date, end_date):

    due_day_midnight = datetime(year=end_date.year, month=end_date.month, day=end_date.day, hour=0, minute=0, second=0)
    time_left_days = (due_day_midnight - start_date).days
    time_left_seconds = (due_day_midnight - start_date).seconds
    hours, remainder = divmod(time_left_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    return time_left_days, hours, minutes, seconds


@client.command(pass_context=True, name='view-daily')
async def view_daily_goals(ctx):

    cnx = mysql.connect(user=MYSQL_USERNAME, host=MYSQL_HOST, database=MYSQL_DB_NAME)
    cursor = cnx.cursor()

    query = ("SELECT * FROM daily ")
    cursor.execute(query)
    # TODO: lump table columns into an array
    # TODO: seperate this code as reused function
    for goal_id, author, description, start_date, status in cursor:
        embed = discord.Embed(title="Daily Goal", color=0x00ff00)
        embed.add_field(name="ID", value=goal_id, inline=False)
        embed.add_field(name="AUTHOR", value=author, inline=False)
        embed.add_field(name="DESC", value=description, inline=False)
        embed.add_field(name="START", value=start_date, inline=False)
        embed.add_field(name="STATUS", value=status, inline=False)

        await client.send_message(ctx.message.channel, embed=embed)

    cursor.close()
    cnx.close()


@client.command(pass_context=True, name='view-sprint')
async def view_sprint_goals(ctx):
    cnx = mysql.connect(user=MYSQL_USERNAME, host=MYSQL_HOST, database=MYSQL_DB_NAME)
    cursor = cnx.cursor()

    query = ("SELECT * FROM sprint ")
    cursor.execute(query)
    # TODO: lump table columns into an array
    # TODO: seperate this code as reused function
    for goal_id, author, description, start_date, status in cursor:
        embed = discord.Embed(title="Sprint Goal", color=0x00ff00)
        embed.add_field(name="ID", value=goal_id, inline=False)
        embed.add_field(name="AUTHOR", value=author, inline=False)
        embed.add_field(name="DESC", value=description, inline=False)
        embed.add_field(name="START", value=start_date, inline=False)
        embed.add_field(name="STATUS", value=status, inline=False)

        await client.send_message(ctx.message.channel, embed=embed)

    cursor.close()
    cnx.close()


@client.command(pass_context=True, name='view-all')
async def view_all_goals(ctx):
    cnx = mysql.connect(user=MYSQL_USERNAME, host=MYSQL_HOST, database=MYSQL_DB_NAME)
    cursor = cnx.cursor()

    query = ("SELECT * FROM daily ")
    cursor.execute(query)
    # TODO: lump table columns into an array
    # TODO: seperate this code as reused function
    for goal_id, author, description, start_date, status in cursor:
        embed = discord.Embed(title="Daily Goal", color=0x00ff00)
        embed.add_field(name="ID", value=goal_id, inline=False)
        embed.add_field(name="AUTHOR", value=author, inline=False)
        embed.add_field(name="DESC", value=description, inline=False)
        embed.add_field(name="START", value=start_date, inline=False)
        embed.add_field(name="STATUS", value=status, inline=False)

        await client.send_message(ctx.message.channel, embed=embed)

    query = ("SELECT * FROM sprint ")
    cursor.execute(query)
    # TODO: lump table columns into an array
    # TODO: seperate this code as reused function
    for goal_id, author, description, start_date, status in cursor:
        embed = discord.Embed(title="Sprint Goal", color=0x00ff00)
        embed.add_field(name="ID", value=goal_id, inline=False)
        embed.add_field(name="AUTHOR", value=author, inline=False)
        embed.add_field(name="DESC", value=description, inline=False)
        embed.add_field(name="START", value=start_date, inline=False)
        embed.add_field(name="STATUS", value=status, inline=False)

        await client.send_message(ctx.message.channel, embed=embed)

    cursor.close()
    cnx.close()


client.run(TOKEN)
