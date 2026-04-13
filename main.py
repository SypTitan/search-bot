import datetime as dt
import io
import json
import os

import disnake
import dotenv
from disnake.ext import commands

import ah
import httpcat
import jsonstorage as storage
import qr
import wolfram

dotenv.load_dotenv()
bot_token = os.environ.get('TOKEN')
run_flask = os.environ.get('RUNFLASK', 'False') == 'True'

if run_flask:
    import keepalive
    keepalive.keep_alive()
    print("Flask server started")

intents = disnake.Intents.default()
bot = commands.Bot(intents=intents,command_prefix=disnake.ext.commands.when_mentioned, reload=True)

@bot.event
async def on_ready():
    print(f"Bot started as {bot.user}")
        
@bot.slash_command(name="writestorage", description="Writes a value to the storage", guild_ids=[1021316997709049886])
async def addtostorage(inter: disnake.ApplicationCommandInteraction, key: str, value: str):
    stored = storage.read()
    stored[key] = value
    storage.write(stored)
    await inter.response.send_message("Value added to storage")
    
@bot.slash_command(name="readstorage", description="Reads the entire storage", guild_ids=[1021316997709049886])
async def readstorage(inter: disnake.ApplicationCommandInteraction):
    stored = storage.read()
    await inter.response.send_message(stored)

@bot.slash_command(name="appiesearch", description="Searches the AH catalog for an item")
async def appiesearch(inter: disnake.ApplicationCommandInteraction, item: str, sort: ah.Sorts = ah.Sorts.Relevance):
    """
    Search the AH catalog for an item

    Parameters
    ----------
    item: The item to search for
    sort: The way to sort the result
    """
    
    await inter.response.defer()
    
    try:
        ah_token = ah.get_token()    
    except ConnectionError as e:
        await inter.followup.send("Error while fetching token: "+str(e))
        return
    
    try:
        search = ah.get_search(ah_token[0], item, sort)
        if len(search) == 0:
            await inter.followup.send("No results found for " + item)
            return
        top_product = search[0]
        while top_product['isSponsored']:
            search = search[1:]
            if len(search) == 0:
                await inter.followup.send("No results found for " + item)
                return
            top_product = search[0]
            
    except ConnectionError as e:
        await inter.followup.send("Error while fetching search: "+str(e))
        return
    
    keysToCheck = ['title','salesUnitSize', 'descriptionHighlights', 'images', 'webshopId']
    if (not (set(keysToCheck) <= set(top_product.keys()))):
        print("Error whilst searching for " + item + ".")
        print("Missing key(s): " + str(set(keysToCheck) - set(top_product.keys())))
        await inter.followup.send("Bot ran into an issue while searching for " + item + ".\nPlease contact SypTitan")
        return
    
    title = top_product['title'] + " " + top_product['salesUnitSize']
    
    if ({'currentPrice','priceBeforeBonus'} <= set(top_product.keys())):
        title += " - ~~€" + str(top_product['priceBeforeBonus']) + "~~  €" + str(top_product['currentPrice'])
    elif ('currentPrice' in top_product.keys()):
        title += " - €" + str(top_product['currentPrice'])
    else:
        title += " - €" + str(top_product['priceBeforeBonus'])
    
    description = top_product['descriptionHighlights'].replace('<p>', '').replace('</p>', '\n').replace('<ul>', '').replace('</ul>', '').replace('<li>', '* ').replace('</li>', '\n')
    embed = disnake.Embed(title=title, description=description, color=0x179eda)
    
    if (top_product['isBonus']):
        if (len(top_product['discountLabels']) > 0):   
            actions = ["* " + x['defaultDescription'].lower().replace("voor €", "voor ").replace("voor ", "voor €")+"\n" for x in top_product['discountLabels']]
        else:
            actions = top_product['discountLabels'][0]['defaultDescription'].lower().replace("voor €", "voor ").replace("voor ", "voor €")
        embed.color = 0xff641e
        embed.add_field(name="In de bonus:", value=''.join(actions), inline=False)
        
    embed.set_image(url=top_product['images'][0]['url'])
    embed.url = "https://www.ah.nl/producten/product/" + str(top_product['webshopId'])
    if 'unitPriceDescription' in top_product.keys():
        embed.set_footer(text=top_product['unitPriceDescription'])
    await inter.followup.send(embed=embed)

@bot.slash_command(name="createqr", description="Creates a QR code for the given text")
async def createqr(inter: disnake.ApplicationCommandInteraction, url: str, size: commands.Range[int, 10, 1000] = 250, ecc: qr.Ecc = qr.Ecc.Low, margin: commands.Range[int, 0, 50] = 2):
    """
    Creates a QR code for the given text

    Parameters
    ----------
    url: The url to link to
    size: The size of the QR code in pixels
    ecc: The error correction level of the QR code
    margin: The margin around the QR code in pixels
    """

    await inter.response.defer()

    original_url = url
    url = qr.format_link(url)

    if not qr.test_url(url):
        failembed = disnake.Embed(title="QR code failed to generate", description="Please use a valid url", color=0xff0000)
        await inter.followup.send(embed=failembed)
        return

    try:
        qr_raw = qr.get_qr(url, size, ecc=ecc, margin=margin)
    except ConnectionError as e:
        await inter.followup.send("Error while creating QR code: "+str(e))
        return
    if (type(qr_raw) in (tuple,list)):
        qr_raw = qr_raw[0]
    buffer = io.BytesIO(qr_raw)
    png = disnake.File(buffer, filename=f"qr.png", description=f"A qr linking to {original_url}")
    embed = disnake.Embed(title="QR code for "+original_url, color=0xffffff)
    embed.url = url
    embed.set_image("attachment://qr.png")

    await inter.followup.send(file=png, embed=embed)
        
@bot.slash_command(name="httpcat", description="Shows a cat picture explaining a HTTP code")
@commands.install_types(guild=True, user=True)
@commands.contexts(guild=True, bot_dm=True, private_channel=True)
async def fetchhttpcat(inter: disnake.ApplicationCommandInteraction, code: commands.Range[int, 100, 599], private: bool = False):  
    """Fetches a cat picture explaining a HTTP code


    Parameters:
    ----------
    code: The HTTP code to look up
    private: Whether the cat should be sent just to you
    """
    
    cat: bytes|str = httpcat.get_cat(code)
    if (type(cat) == str):
        await inter.response.send_message(cat, ephemeral=True)
        return
        
    await inter.response.defer(ephemeral=private)
    buffer = io.BytesIO(cat)
    
    jpg = disnake.File(buffer, filename=f"httpcat_{code}.jpg", description=f"A cat explaining HTTP code {code}")
    embed = disnake.Embed(title=f"HTTP code {code}", color=0x179eda)
    embed.set_image(f"attachment://httpcat_{code}.jpg")
    
    await inter.followup.send(file=jpg, embed=embed)
    
@bot.slash_command(name="wolfram", description="Looks up a query on Wolfram|Alpha")
@commands.install_types(guild=True, user=True)
@commands.contexts(guild=True, bot_dm=True, private_channel=True)
async def wolframquery(inter: disnake.ApplicationCommandInteraction, query: str, private: bool = False):
    """Looks up a query on Wolfram|Alpha

    Parameters:
    ----------
    query: The query to look up
    private: Whether the response should be sent from just you
    """
    
    await inter.response.defer(ephemeral=private)
    
    response = wolfram.get_answer(query)
    
    # embed = disnake.Embed(title=query, description=response, color=0xFD7D01)
    
    message = f"*{query}* is **{response}**"
    
    await inter.followup.send(message)
    
    
# @bot.slash_command(name="upload", description="Uploads a file to the null pointer hoster")
# @commands.install_types(guild=True, user=True)
# @commands.contexts(guild=True, bot_dm=True, private_channel=True)
# async def nullupload(inter: disnake.ApplicationCommandInteraction, file: disnake.Attachment, private: bool = False,  expiry: int = commands.Param(0, gt=0)):
#     """Uploads a file to the null pointer hoster

#     Parameters
#     ----------
#     file: The file you want to upload. Maximum discord file size applies
#     private: Whether the link should be sent just to you
#     expiry: The time in hours the link should be valid for
#     """
    
#     print(file.url)
    
#     await inter.response.send_message("pong")

bot.run(bot_token)
