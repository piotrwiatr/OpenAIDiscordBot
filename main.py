import discord
import os
import openai


client = discord.Client(intents=discord.Intents.default())
TOKEN = os.getenv("DISCORD_TOKEN")
openai.api_key = os.getenv("OPENAI_TOKEN")

# splices text to get around discord character limit

def spliceText(message, addFormat=False):
    discordCharLimit = 1900  # minus 100 characters just to make sure.
    returnMessages = []

    while len(message) > discordCharLimit:
        msgToAppend = message[:discordCharLimit]
        if addFormat:
            msgToAppend = "```" + msgToAppend + "```"
        returnMessages.append(msgToAppend)
        message = message[discordCharLimit:]

    if message != "":
        msgToAppend = message
        if addFormat:
            msgToAppend = "```" + msgToAppend + "```"
        returnMessages.append(msgToAppend)

    return returnMessages

def sendChatRequest(message):
    text = message.split("<@1049857759643971685> chat")
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo",
                                        messages=[{"role": "user", "content": text[1]}],
                                        temperature=0.9,
                                        max_tokens=4000)
    response = response["choices"][0]["message"]["content"]
    return spliceText(response)

def sendTextRequest(message):
    text = message.split("<@1049857759643971685> text")
    response = openai.Completion.create(
                                        model="text-davinci-003",
                                        prompt=text[1],
                                        max_tokens=2048,
                                        temperature=0
                                        )
    response = response["choices"][0]["text"]
    return spliceText(response)

def sendCodeRequest(message):
    text = message.split("<@1049857759643971685> code")
    response = openai.Completion.create(model="code-davinci-002",
                                        prompt=text[1],
                                        max_tokens=2000,
                                        temperature=0
                                        )
    response = response["choices"][0]["text"]
    return spliceText(response, True) 

def sendImageRequest(message):
    text = message.split("<@1049857759643971685> image")
    try:
        response = openai.Image.create(prompt=text[1], n=1, size="512x512")
        response = response['data'][0]['url']
    except openai.error.InvalidRequestError:
        response = "You just tried to be a bit too edgy, eh? You think you can just type any keyword and get a result. Well, guess what, you can't."
    else:
        return response
    
@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('<@1049857759643971685> chat'):
        messagesToSend = sendChatRequest(message.content)
        for msg in messagesToSend:
            await message.channel.send(msg)

    elif message.content.startswith('<@1049857759643971685> text'):
        messagesToSend = sendTextRequest(message.content)
        for msg in messagesToSend:
            await message.channel.send(msg)

    elif message.content.startswith('<@1049857759643971685> image'):
        messageToSend = sendImageRequest(message.content)
        await message.channel.send(messageToSend)

    elif message.content.startswith('<@1049857759643971685> code'):
        messagesToSend = sendCodeRequest(message.content)
        for msg in messagesToSend:
            await message.channel.send(msg)

    elif message.content.startswith('<@1049857759643971685> help'):
        await message.channel.send(
            "Hello, I\'m a custom discord bot that uses the OpenAI api to generate text and images. To generate text, please type the following command: \n<@1049857759643971685> text {prompt}.\nTo generate an image, please type the following command: \n<@1049857759643971685> image {prompt}\nTo generate code, please type the following command:\n<@1049857759643971685> code {prompt}\nTo chat with ChatGPT instead, please type the following command:\n<@1049857759643971685> chat {prompt}\nNote, the current OpenAI model for code completion just returns a random stack overflow article LOL"
        )

client.run(TOKEN)
