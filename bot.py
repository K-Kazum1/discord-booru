from discord.ext import commands
import asyncio,discord
import datetime,os,json,re,random
bot = commands.Bot(command_prefix='!')
try:
    Images=json.load(open('data.json','r'))
    Images={i:set(Images[i]) for i in Images}
except:
    Images={}
    
with open('config.txt','r') as f:
    token=f.readline()[7:-2]
    archive_channel=[f.readline()[12:-1]]
    admin=f.readline()[10:-2]


def jsonify(tags={},filedir=''):
    date=datetime.datetime.now()

    tags.add(str(date.year))
    tags.add(str(date.day))
    tags.add("Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split(' ')[date.month-1])
    tags.add("January Febuary March April May June July August September October November December".split(' ')[date.month-1])

    tags={i.lower() for i in tags}

    return tags

def messagepicker(tags):
    try:
        messages={}
        curtag=''
        with open('messages.txt') as f:
            while f:
                cur=f.readline()
                if not cur:
                    break
                if cur[-2]==':':
                    curtag=cur[:-2]
                    cur=f.readline()
                    
                if curtag in messages:
                    messages[curtag].append(cur)
                else:
                    messages[curtag]=[cur]
        potential=messages['']
        for i in messages:
            if i in tags:
                potential+=messages[i]
        return random.choice(potential)
    except Exception as e:
        print(e)        

async def sendfiles(channel,files,embeds=[],archive=False):
    
    embeds='\n'.join(list(embeds)[:5])
    if len(files)==1:
        await channel.send(embeds,file=discord.File(f'images/{list(files)[0]}'))
    elif files:
        await channel.send(embeds,files=[discord.File(f'images/{i}') for i in files][:5])
    elif embeds:
        await channel.send(embeds)
    elif not archive:
        await channel.send("no match")

@bot.command()
async def home(ctx, *arg):
    global admin
    if ctx.author.id == admin:
        with open('config.txt','w') as f:
            global token
            f.write(f'token="{token}"\n')
            f.write(f'channel_id="{ctx.channel.id}"')
        global archive_channel
        archive_channel=[bot.get_channel(int(ctx.channel.id))]
        await ctx.send("Archive set")
    else:
        await ctx.send("You're not the admin")
        
bot.remove_command('help')
@bot.command()
async def intro(ctx, *arg):
    text=''
    for i in open('help.txt','r'):
        text+=i
    await ctx.send(f'```{text}```')
@bot.command()
async def archive(ctx, *arg):

    
    filedir=f'{ctx.message.guild}'
    filenames=[]
    try:os.makedirs(f'images/{filedir}')
    except:pass


    for image in ctx.message.attachments:

        dirfilenames=os.listdir(f'images/{filedir}')
        f=image.filename

        if f in dirfilenames:
            c=1
            fs=f[:f.index('.')]
            fe=f[f.index('.'):]
            while f'{fs}{c}{fe}' in dirfilenames:c+=1

            f=f'{fs}{c}{fe}'

        filename=f'{filedir}/{f}'
        filenames.append(filename)
        
        await image.save(f'images/{filename}')
        
            
        Images[filename]=jsonify(set(arg),filedir)
    for embeds in ctx.message.embeds:
        arg=list(arg)
        arg.remove(embeds.thumbnail.url)
        Images[embeds.thumbnail.url]=jsonify(set(arg),filedir)

    
    global archive_channel
    if archive_channel:        
        await sendfiles(archive_channel[0],filenames,embeds=[i.thumbnail.url for i in ctx.message.embeds],archive=True)
    await ctx.send(messagepicker(arg))

    json.dump({i:list(Images[i]) for i in Images},open('data.json','w'))
            
embeds  =   lambda message:'\n'.join([f'[{("" if i.thumbnail.url==discord.Embed.Empty else f"<Image: {i.thumbnail.url}>")+("" if i.description==discord.Embed.Empty else f"<Text: {i.description}>")}]' for i in message.embeds])
attachments = lambda message:'\n'.join([f'[Image: {i.url}]' for i in message.attachments])
   
@bot.command()
async def load(ctx,*arg):
    results=Images

    for i in arg:
        i=i.lower()
        results={j:results[j] for j in results if i in results[j]}

    print(f"found {len(results)} results with tags {arg}")

    
    embeds={j:results[j] for j in results if not  os.path.isfile('images/'+j)}
    results={j:results[j] for j in results if os.path.isfile('images/'+j)}
    await sendfiles(ctx,results,embeds)

@bot.event
async def on_ready():
    try:
        global archive_channel    
        archive_channel=[bot.get_channel(int(archive_channel[0]))]
        print(f"Archive channel set as {archive_channel[0].name} in {archive_channel[0].guild}")
    except:
        archive_channel.pop(0)
        print("No archive channel set. Did you either forget to set one, or do it incorrectly?")
    print("ready")
@bot.event
async def on_message(message):
    if not message.author.bot:
        await bot.process_commands(message)
    
@bot.event
async def on_message_edit(before,after):
    if before.clean_content==after.clean_content and before.embeds!=after.embeds:
        await on_message(after)


try:
    bot.run(token)
except discord.errors.LoginFailure:
    print("The bot token seems to be wrong")


input("")
