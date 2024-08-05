import os, discord
from dotenv import load_dotenv

#Import for web sync
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

# Charger les var depuis .env
load_dotenv()
#credit.json
cred = credentials.Certificate({
  "type" : os.getenv("type"),
  "project_id": os.getenv("project_id"),
  "private_key_id": os.getenv("private_key_id"),
  "private_key": os.getenv("private_key"),
  "client_email": os.getenv("client_email"),
  "client_id": os.getenv("client_id"),
  "auth_uri": os.getenv("auth_uri"),
  "token_uri": os.getenv("token_uri"),
  "auth_provider_x509_cert_url": os.getenv("auth_provider_x509_cert_url"),
  "client_x509_cert_url": os.getenv("client_x509_cert_url"),
  "universe_domain": os.getenv("universe_domain")
})
firebase_admin.initialize_app(cred, {
  "databaseURL": "https://snifsnoufdataconnect-default-rtdb.europe-west1.firebasedatabase.app/",
})
ref = db.reference('/')  # starting point

bot_prefix = "!"

def syncroFireBase(currList):
    for index,name in enumerate(currList):
        ref.child(str(index)).set(name)

def tryAddElem(newElem,currList):
    added = False
    dList = list(currList)
    if newElem not in dList:
        added = True
        dList.append(newElem)
    return dList,added

def createBat(currList):
    with open("macro.bat",'w') as batFile:
        listStringSpace = ""
        for name in currList:
            listStringSpace+="{} ".format(name)
        batFile.write('@echo off\nsetlocal\nset "list={}"'.format(listStringSpace))
        batFile.write('\nfor %%i in (%list%) do (\n\tstart "" "https://www.instant-gaming.com/fr/giveaway/%%i"\n)')
        batFile.write('\nendlocal\nexit')



async def snifSnoufFct(message):

    mainList = ref.get()
    if message.content == bot_prefix+'list': # Affiche la liste en clair
        disString =""
        for name in mainList:
            disString += "{}\n".format(name)
        await message.channel.send('Voici la liste des partenaires :\n{}'.format(disString))

    if message.content.startswith(bot_prefix+'addList'): # Ajoute une valeur à la liste si elle est pas déjà ajoutée
        newName = message.content.replace(bot_prefix+'addList ',"").upper()
        mainList,added = tryAddElem(newName,mainList)

        displayString = "Element ajouté. Merci !" if added else "Element déjà présent"
        await message.channel.send(displayString)

    if message.content == bot_prefix+'webList': # Donne le lien du site
        await message.channel.send('Le site est : https://caimez323.github.io/src/snifsnouf.html')
    
    if message.content == bot_prefix+'listMacro': # Crée un fichier macro à DL qui ouvre tout
        createBat(mainList)
        attachment = discord.File("macro.bat")
        await message.channel.send(file=attachment,content='Liste Macro créée')

    if message.content == bot_prefix+'isWebUp' or message.content == bot_prefix+'iwu':
        displayString = "Database local non syncronisée" if ref.get() != mainList else "Les databases sont syncros"
        await message.channel.send(displayString)

    if message.content == bot_prefix+'dataSync':
        await message.channel.send("Syncronisation.... (cela peut prendre quelques secondes)")
        syncroFireBase(mainList)
        await message.channel.send("Données du bot syncronisées avec le site")
    
    if message.content == bot_prefix+"snifHelp":
        displayString = "Liste des commandes : \n"
        displayString +="> **{}list** : permet de lister les créateurs déjà enregistrés \n".format(bot_prefix)
        displayString +="> **{}addList** : permet d'ajoute un créateur à la liste\n".format(bot_prefix)
        displayString +="> **{}webList** : permet de donner le site internet\n".format(bot_prefix)
        displayString +="> **{}macro** : permet de générer une macro téléchargeable pour tout ouvrir d'un coup\n".format(bot_prefix)
        displayString +="> **{}iwu** : permet de voir si la database est syncro avec le snifSnouf\n".format(bot_prefix)
        displayString +="> **{}dataSync** : permet de syncroniser\n".format(bot_prefix)
        await message.channel.send(displayString)

