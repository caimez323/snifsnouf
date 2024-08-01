import os
import discord
import json
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup

#Import for web sync
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

#credit.json
cred = credentials.Certificate('var/config.json')
firebase_admin.initialize_app(cred, {
  "databaseURL": "https://snifsnoufdataconnect-default-rtdb.europe-west1.firebasedatabase.app/",
})
ref = db.reference('/')  # starting point


def count_a_tags(url):
    try:
        response = requests.get(url)
        response.raise_for_status()

        # Parser le contenu HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        a_tags = soup.find_all('a')
        return len(a_tags)
    
    except requests.RequestException as e:
        print(f"Une erreur est survenue : {e}")
        return 0
    
def isWebsiteUp(currList):
    return len(currList) == count_a_tags("https://caimez323.github.io/src/snifsnouf.html")


# Charger le token depuis le fichier .env
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Créer une instance de client Discord
intents = discord.Intents.default()
intents.message_content = True  # Pour permettre de lire le contenu des messages

client = discord.Client(intents=intents)

bot_prefix = "$"

#Au démarrage on load ce qui existe déjà dans la liste, 
#Quand on tape une commande, on vient regarder dans la liste ici, et si besoin on rajoute dans le mainList.json en l'écrasant complètement


def syncroFireBase(currList):
    for index,name in enumerate(currList):
        ref.child(str(index)).set(name)

def initList():
    with open("mainList.json","r") as jsonFile:
        dataMain = json.load(jsonFile)["main"]
    return dataMain

def tryAddElem(newElem,currList):
    added = False
    dList = list(currList)
    if newElem not in dList:
        added = True
        dList.append(newElem)
    return dList,added


def overwriteList(currList):
    payload = {"main": currList}
    with open("mainList.json","w") as jsonFile:
        json.dump(payload,jsonFile,indent=4)

def createBat(currList):
    with open("macro.bat",'w') as batFile:
        listStringSpace = ""
        for name in currList:
            listStringSpace+="{} ".format(name)
        batFile.write('@echo off\nsetlocal\nset "list={}"'.format(listStringSpace))
        batFile.write('\nfor %%i in (%list%) do (\n\tstart "" "https://www.instant-gaming.com/fr/giveaway/%%i"\n)')
        batFile.write('\nendlocal\nexit')


mainList = initList()
print(len(mainList))

@client.event
async def on_ready():
    print(f'{client.user} s\'est connecté !')

@client.event
async def on_message(message):
    global mainList
    # Ne pas répondre à soi-même
    if message.author == client.user:
        return

    if message.content == bot_prefix+'list': # Affiche la liste en clair
        disString =""
        for name in mainList:
            disString += "{}\n".format(name)
        await message.channel.send('Voici la liste des partenaires :\n{}'.format(disString))

    if message.content.startswith(bot_prefix+'addList'): # Ajoute une valeur à la liste si elle est pas déjà ajoutée
        newName = message.content.replace(bot_prefix+'addList ',"").upper()
        mainList,added = tryAddElem(newName,mainList)
        if added: overwriteList(mainList)

        displayString = "Element ajouté. Merci !" if added else "Element déjà présent"
        await message.channel.send(displayString)

    if message.content == bot_prefix+'webList': # Donne le lien du site
        await message.channel.send('Le site est : https://caimez323.github.io/src/snifsnouf.html')
    
    if message.content == bot_prefix+'listMacro': # Crée un fichier macro à DL qui ouvre tout
        createBat(mainList)
        attachment = discord.File("macro.bat")
        await message.channel.send(file=attachment,content='Liste Macro créée')

    if message.content == bot_prefix+'isWebUp' or message.content == bot_prefix+'iwu':
        displayString = "Site web à jour" if isWebsiteUp(mainList) else "Le site n'est pas à jour, appelez Batman"
        await message.channel.send(displayString)
    #TODO CHANGE ACCORDING TO DATAS IN FIREBASE DATABASE RATHER THAN SCRAPPING

    if message.content == bot_prefix+'dataSync':
        syncroFireBase(mainList)
        await message.channel.send("Données du bot syncronisées avec le site")
    

# Lancer le bot
client.run(TOKEN)
