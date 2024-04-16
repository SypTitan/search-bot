import disnake, dotenv, os, json
from disnake.ext import commands
import datetime as dt
import jsonstorage as storage
import ah

dotenv.load_dotenv()
bot_token = os.environ.get('TOKEN')

intents = disnake.Intents.default()
bot = commands.Bot(intents=intents,command_prefix=disnake.ext.commands.when_mentioned)

@bot.event
async def on_ready():
    print(f"Bot started as {bot.user}")
        
@bot.slash_command(name="writestorage", description="Writes a value to the storage", guild_ids=[1021316997709049886])
async def addtostorage(inter: disnake.ApplicationCommandInteraction, key: str, value: str):
    stored = await storage.read()
    stored[key] = value
    await storage.write(stored)
    await inter.response.send_message("Value added to storage")
    
@bot.slash_command(name="readstorage", description="Reads the entire storage", guild_ids=[1021316997709049886])
async def readstorage(inter: disnake.ApplicationCommandInteraction):
    stored = await storage.read()
    await inter.response.send_message(stored)

@bot.slash_command(name="appiesearch", description="Searches the AH catalog for an item")
async def appiesearch(inter: disnake.ApplicationCommandInteraction, item: str, sort: ah.sorts = ah.sorts.Relevance):
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
    
    if ('currentPrice' in top_product.keys()):
        title = top_product['title'] + " " + top_product['salesUnitSize'] + " - ~~€" + str(top_product['priceBeforeBonus']) + "~~  €" + str(top_product['currentPrice'])
    else:
        title = top_product['title'] + " " + top_product['salesUnitSize'] + " - €" + str(top_product['priceBeforeBonus'])
    description = top_product['descriptionHighlights'].replace('<p>', '').replace('</p>', '\n').replace('<ul>', '').replace('</ul>', '').replace('<li>', '* ').replace('</li>', '\n')
    embed = disnake.Embed(title=title, description=description, color=0x179eda)
    
    if (top_product['isBonus']):
        if (len(top_product['discountLabels']) > 0):   
            actions = ["* " + x['defaultDescription'].lower().replace("voor €", "voor ").replace("voor ", "voor €")+"\n" for x in top_product['discountLabels']]
        else:
            actions = top_product['discountLabels'][0]['defaultDescription'].lower().replace("voor €", "voor ").replace("voor ", "voor €")
        embed.add_field(name="In de bonus:", value=''.join(actions), inline=False)
        
    embed.set_image(url=top_product['images'][0]['url'])
    embed.url = "https://www.ah.nl/producten/product/" + str(top_product['webshopId'])
    if 'unitPriceDescription' in top_product.keys():
        embed.set_footer(text=top_product['unitPriceDescription'])
    await inter.followup.send(embed=embed)

bot.run(bot_token)