
from twilio.rest import Client


#envia msg para whatsapp
def enviaMsg(msg,num):

    # Your Account Sid and Auth Token from twilio.com/console
    # DANGER! This is insecure. See http://twil.io/secure
    account_sid = 'ACf359d87d80dec8e234eb846a8401d673'
    auth_token = '754c82f5670c5935e1805b1d0af8499c'


    client = Client(account_sid, auth_token)

    message = client.messages.create(
                                body=msg,
                                #body='Você enviou: ' + msg + '\nSeu numero é: ' + num,
                                #media_url=['https://demo.twilio.com/owl.png'],
                                from_='whatsapp:+14155238886',
                                to = num
                                #to = 'whatsapp:+558896382571'
                              )

    print(message.sid)
    #return(message.sid) #tambem funciona
