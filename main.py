import discord
import asyncio
import json
import os
from discord.ext import commands
from config import settings


prefix = settings['PREFIX']
intents = discord.Intents.all()
client = discord.Client(intents=intents)
client = commands.Bot(command_prefix = settings['PREFIX'], intents=intents)
client.remove_command('help')


@client.event
async def on_ready():
    print (f"Залогинелся как {settings['NAME BOT']}")


# Help
@client.command(aliases = ['Help', 'help', 'HELP', 'hELP', 'хелп', 'Хелп', 'ХЕЛП', 'хЕЛП'])
async def __help (ctx):
    emb = discord.Embed( title = 'ДОСТУПНЫЕ КОМАНДЫ:', description = 'Бот для тестового задания!', colour = discord.Color.green() )
    emb.add_field( name = 'Информация', value = f'`{prefix}help`', inline=False)
    emb.add_field( name = 'Модерирование', value = f'`{prefix}ban` `{prefix}unban` `{prefix}kick` ', inline=False)
    await ctx.send ( embed = emb)
    print(f'[Logs:info] Справка по командам была успешно выведена | {prefix}help ')


#Welcome
class Welcome(commands.Cog):
    def __init__(self, client):
        self.client=client

    @commands.Cog.listener()
    async def on_ready(self):
        print("Welcome: ON")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = member.guild.system_channel
        await channel.send(embed = discord.Embed( description = f'{member.mention} connected to the channel'))

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        channel = member.guild.system_channel
        await channel.send(embed = discord.Embed( description = f'{member.mention} left channel'))
client.add_cog(Welcome(client))


#Kick
@client.command(aliases = ['кик', 'Кик', 'кИК', 'КИК', 'Kick', 'kICK', 'KICK', 'kick'])
@commands.has_permissions ( administrator = True )
async def __kick(ctx, member: discord.Member, *, reason = None):
    await ctx.message.add_reaction('✅') 
    await member.kick( reason = reason ) 
    emb = discord.Embed( title = 'kick', description = f'Пользователь {member}  был кикнут по причине { reason } ', colour = discord.Color.green() )

    await ctx.send( embed = emb )

    print(f'[Logs:moderation] Пользователь {member} был кикнут по причине {reason} | {prefix}kick ')

@__kick.error
async def kick_error(ctx, goodbye):
    if isinstance ( goodbye, commands.MissingRequiredArgument):
        emb = discord.Embed( title = f'**Команда "{prefix}кик"**', description = f'Изгоняет указаного участника с сервера с возможностью возвращения ', colour = discord.Color.green() )
        emb.set_author(name = ctx.author.name, icon_url = ctx.author.avatar_url)
        emb.add_field( name = 'Использование', value = "!кик <@⁣Участник | ID>", inline=False)
        emb.add_field( name = 'Пример', value = "`!кик @⁣Участник`\n┗ Кикнет указаного участника.", inline=False)
        await ctx.send ( embed = emb)
        print(f"[Logs:error] Необходимо указать участника | {prefix}kick")

    if isinstance (goodbye, commands.MissingPermissions):
        emb = discord.Embed( title = f'**Команда "{prefix}кик"**', description = f'Изгоняет указаного участника с сервера с возможностью возвращения ', colour = discord.Color.green() )
        emb.set_author(name = ctx.author.name, icon_url = ctx.author.avatar_url)
        emb.add_field( name = 'ОШИБКА!', value = "У вас недостаточно прав!", inline=False)
        await ctx.send ( embed = emb)
        print(f"[Logs:Error] [Ошибка доступа] Пользователь [{ctx.author}] попытался кикнуть | {prefix}kick")


@client.command()
async def ban(ctx, member : discord.Member, *, reason=None):
	await member.ban(reason=reason)
	await ctx.send(f'{member.mention} has been banned')

@client.command()
async def unban(ctx, *, member):
	banned_users = await ctx.guild.bans()
	member_name, member_discriminator = member.split('#')

	for ban_entry in banned_users:
		user = ban_entry.user

		if (user.name, user.discriminator) == (member_name, member_discriminator):
			await ctx.guild.unban(user)
			await ctx.send(f'{user.mention} has been unbanned')
			return


#Leveling
with open("users.json", "ab+") as ab:
    ab.close()
    f = open('users.json','r+')
    f.readline()
    if os.stat("users.json").st_size == 0:
      f.write("{}")
      f.close()
    else:
      pass
 
with open('users.json', 'r') as f:
  users = json.load(f)
 
@client.event    
async def on_message(message):
    if message.author.bot == False:
        with open('users.json', 'r') as f:
            users = json.load(f)
        await add_experience(users, message.author)
        await level_up(users, message.author, message)
        with open('users.json', 'w') as f:
            json.dump(users, f)
            await client.process_commands(message)
 
async def add_experience(users, user):
  if not f'{user.id}' in users:
        users[f'{user.id}'] = {}
        users[f'{user.id}']['experience'] = 0
        users[f'{user.id}']['level'] = 0
  users[f'{user.id}']['experience'] += 1
  print(f"{users[f'{user.id}']['level']}")
 
async def level_up(users, user, message):
  experience = users[f'{user.id}']["experience"]
  lvl_start = users[f'{user.id}']["level"]
  lvl_end = int(experience // 20)
  if lvl_start < lvl_end:
    await message.channel.send(f'{user.mention} has promoted level {lvl_end}.')
    users[f'{user.id}']["level"] = lvl_end
 

@client.command(aliases = ['rank'])
async def __rank(ctx, member: discord.Member = None):
  if member == None:
    userlvl = users[f'{ctx.author.id}']['level']
    experience = users[f'{ctx.author.id}']['experience']
    await ctx.send(f'{ctx.author.mention} You are at level {userlvl}, experience - {experience}!')

  else:
    userlvl2 = users[f'{member.id}']['level']
    await ctx.send(f'{member.mention} is at level {userlvl2}!')
 


client.run (settings['TOKEN'])