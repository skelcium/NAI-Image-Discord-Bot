import io
import random
import requests
import time
import zipfile
from typing import Literal

import discord
from discord import app_commands
from discord.ext import commands

endpoint = 'https://api.novelai.net/ai/generate-image'

token = None
with open('./token.txt', 'r') as token_in:
    token = token_in.read().strip()

headers = {
    'authority': 'api.novelai.net',
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9',
    'authorization': token,
    'content-type': 'application/json',
    'origin': 'https://novelai.net',
    'referer': 'https://novelai.net/'
}

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

bot = commands.Bot(intents=intents, command_prefix=('~', '!'), case_insensitive=True)
tree = app_commands.CommandTree(client)


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    await tree.sync()


async def gen(ctx: discord.Interaction, resolution: Literal['wide', 'tall', 'square'],
              model: Literal['safe', 'nai', 'fur'], prompt: str):
    try:
        # Only allow in bot channel
        # if ctx.channel_id != bot_channel_id:
        #	await ctx.response.send_message('Wrong channel NOOB')
        #	return

        print(f"Resolution: {resolution} | Model: {model}")
        banned_words = ["naked armadillo"]
        allow_proceed = True

        for word in banned_words:
            if word in prompt.lower():
                allow_proceed = False

        if not allow_proceed:
            await ctx.response.send_message(random.choice(['That word is banned!', 'erm, CRINGE!', ':/', '._.']))
        else:
            await ctx.response.defer()

            seed = random.randint(0, 4294967295)
            temp_filename = './ai/' + str(int(time.time()))

            json_data = {
                'input': 'masterpiece, best quality, ',
                'model': 'nai-diffusion',  # 'safe-diffusion', 'nai-diffusion', 'nai-diffusion-furry'
                'action': 'generate',
                'parameters': {
                    'width': 512,  # 640
                    'height': 768,  # 640
                    'scale': 11,  # 11.1
                    'sampler': 'k_dpmpp_2m',
                    'steps': 28,
                    'n_samples': 1,
                    'ucPreset': 0,
                    'qualityToggle': True,
                    'seed': 0,
                    'sm': True,
                    'sm_dyn': True,
                    'dynamic_thresholding': False,
                    'controlnet_strength': 1,
                    'legacy': False,
                    'negative_prompt': 'lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry',
                },
            }

            res = (512, 768)
            mod = 'nai-diffusion'

            if resolution == 'wide':
                res = (768, 512)
            elif resolution == 'tall':
                res = (512, 768)
            elif resolution == 'square':
                res = (640, 640)

            if model == 'safe':
                mod = 'safe-diffusion'
            elif model == 'nai':
                mod = 'nai-diffusion'
            elif model == 'fur':
                mod = 'nai-diffusion-furry'

            json_data['model'] = mod
            json_data['seed'] = seed
            json_data['input'] = prompt
            json_data['parameters']['width'] = res[0]
            json_data['parameters']['height'] = res[1]

            r = requests.post('https://api.novelai.net/ai/generate-image', headers=headers, json=json_data)

            print(f"[{r.status_code}] {prompt}: [{seed}]")

            z = zipfile.ZipFile(io.BytesIO(r.content))
            e = {n: z.read(n) for n in z.namelist()}

            if not e:
                return

            print(f"Contents [{len(e)}]: {', '.join(e.keys())}")

            if len(e) > 1:
                print(f"WARNING: File count exceeds 1, additional images may be lost")

            with open(f"{temp_filename}.png", 'wb') as o:
                o.write(e[list(e)[0]])

            file = discord.File(f"{temp_filename}.png")

            embed = discord.Embed(url='')
            embed.set_footer(text=f"📝 {prompt}  •  🗿 {model}  •  🌱 {seed}")
            embed.set_image(url=f"attachment://{temp_filename}")

            await ctx.followup.send(file=file, embed=embed)
    except Exception as ex:
        pass


@tree.command(name='prompt', description='Describe a scenario. e.g. 2 cats eating a burger.')
async def prompt(ctx: discord.Interaction, prompt: str):
    await gen(ctx, 'tall', 'nai', prompt)


@tree.command(name='masterpiece', description='Describe a scenario. e.g. 2 cats eating a burger.')
async def masterpiece(ctx: discord.Interaction, prompt: str):
    await gen(ctx, 'tall', 'nai', 'masterpiece, best quality, ' + prompt)


@tree.command(name='ai', description='Describe a scenario. e.g. 2 cats eating a burger.')
@app_commands.choices(resolution=[
    app_commands.Choice(name='wide', value='wide'),
    app_commands.Choice(name='tall', value='tall'),
    app_commands.Choice(name='square', value='square'),
])
@app_commands.choices(model=[
    app_commands.Choice(name='safe', value='safe'),
    app_commands.Choice(name='nai', value='nai'),
    app_commands.Choice(name='fur', value='fur'),
])
async def ai(ctx: discord.Interaction, resolution: app_commands.Choice[str], model: app_commands.Choice[str],
             prompt: str):
    await gen(ctx, resolution.value, model.value, prompt)


@tree.command(name='aimasterpiece', description='Describe a scenario. e.g. 2 cats eating a burger.')
@app_commands.choices(resolution=[
    app_commands.Choice(name='wide', value='wide'),
    app_commands.Choice(name='tall', value='tall'),
    app_commands.Choice(name='square', value='square'),
])
@app_commands.choices(model=[
    app_commands.Choice(name='safe', value='safe'),
    app_commands.Choice(name='nai', value='nai'),
    app_commands.Choice(name='fur', value='fur'),
])
async def aimasterpiece(ctx: discord.Interaction, resolution: app_commands.Choice[str], model: app_commands.Choice[str],
                        prompt: str):
    await gen(ctx, resolution.value, model.value, 'masterpiece, best quality, ' + prompt)


client.run('')  # CLIENT KEY
