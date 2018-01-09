# Telepot è una libreria molto semplice per creare dei bot Telegram senza troppe pretese
# -> per cose più complesse usare altri framework
from datetime import timedelta
from datetime import datetime
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from calendar_keyboard import create_calendar
from calendar_keyboard import search_calendar
from config import TOKEN  # generato da BotFather alla creazione del bot
                          # è da tenere privato perchè è la chiave di accesso al bot -> chiunque ce l'ha può apportare modifiche
                          # questo è il motivo per cui è inserito in un file esterno (da tenere privato)
import datetime, time
import telepot

aperto = 0
nome_apertura = ""
ora_apertura = ""
stato_apertura = 0
current_shown_dates={}
#GOOGLE_API_TOKEN = "AIzaSyAr6iDk6svV8CSHfVA4smnPVpR0mjnLwog"


             
def on_chat_message(msg):
    #glance è la funzione per il parsing dei messaggi (che sono degli oggetti JSON)
    #è importante verificare questi 3 parametri per capire come reagire
    #chat_id in particolare è molto importante perchè permette di identificare l'utente che ha inviato il messaggio
    #-> identifica la chat alla quale fare riferimento e a cui rispondere
    content_type, chat_type, chat_id = telepot.glance(msg)
    global aperto   #global serve ad aggiornare la variabile ad ogni ciclo della funzione
                    #->senza questa parola chiave 'aperto' sarebbe vista con scope locale quindi si perderebbero
                    #le modifiche tra una chiamata e l'altra e non si terrebbe traccia dell'apertura/chiusura
    global nome_apertura, ora_apertura, stato_apertura, current_shown_dates
    if content_type == 'text':
       txt = msg['text']
       
    #Per i COMANDI: MODIFICARE QUI quando se ne aggiunge uno nuovo
    #python nativamente non prevede un costrutto del tipo switch-case
    #si ricorre a una cascata di if-elif per distinguere i vari comandi
       if txt.startswith('/start'):
            bot.sendMessage(chat_id, 'Ciao, benvenuto nel bot di JEToP!')  #funzione che permette al bot di rispondere a chi lo ha interrogato (chat_id)


       elif txt.startswith('/ufficio_aperto'):
           if(aperto > 0):
            bot.sendMessage(chat_id, 'Ufficio aperto da {} alle {}'.format(nome_apertura, ora_apertura))
           else:
            bot.sendMessage(chat_id, 'Ufficio attualmente chiuso')

            
       elif txt.startswith('/apri_ufficio'):
           if (aperto > 0):
            bot.sendMessage(chat_id, 'L\'ufficio è già stato aperto da {}!'.format(nome_apertura))
           else:
             bot.sendMessage(chat_id, 'Ok. Ora inserisci il tuo nome!')
             stato_apertura = 1;
             
                        
       elif txt.startswith('/chiudi_ufficio'):
         if(aperto > 0):
            aperto = 0             
            bot.sendMessage(chat_id, 'Ok! Ho chiuso l\'ufficio')
         else:
            bot.sendMessage(chat_id, 'L\'ufficio è già chiuso!')

            
       elif txt.startswith('/help'):
            bot.sendMessage(chat_id, 'Ecco i comandi che capisco:\n\n'+
                            '/start Avvia il bot\n\n'+
                            '/ufficio_aperto Verifica se l’ufficio è stato aperto da qualcuno\n\n'+
                            '/apri_ufficio Permette di aprire l’ufficio inserendo il proprio nome \n\n'+
                            '/chiudi_ufficio Permette di chiudere l’ufficio \n\n'+
                            '/impegni_calendar Visualizza gli impegni della giornata \n\n'+
                            '/cerca_impegni_calendar Visualizza gli impegna della giornata selezionata dal calendario\n\n')

       elif txt.startswith('/impegni_calendar'):
            today = datetime.datetime.now()
            #today_range = datetime.datetime.now()+timedelta(2)
            today_morning = today.strftime('%Y-%m-%dT') + "00:00:00." + today.strftime("%S")+'Z' # 'Z' indica il fuso orario (UTC)
            today_evening = today.strftime('%Y-%m-%dT') + "23:59:59."  + today.strftime("%S")+'Z'
            message = search_calendar(today_morning, today_evening)
            bot.sendMessage(chat_id, message, parse_mode = 'Markdown')
         
                     
       elif txt.startswith('/cerca_impegni_calendar'):
           
           now = datetime.datetime.now() #Data corrente
           date = (now.year,now.month)
           current_shown_dates[chat_id] = date #Salvo la data corrente in un dizionario. Servirà poi per fare la ricerca degli eventi
           keyboard = create_calendar(now.year,now.month)
           bot.sendMessage(chat_id, "Scegli una data", reply_markup=keyboard)
           
             
       else:
           if (stato_apertura == 1):
            params = txt.split()
            if len(params) == 0:
             bot.sendMessage(chat_id, 'Non hai inserito il tuo nome!')
            else:
             aperto = 1
             i = datetime.datetime.now()
             ora_apertura = i.strftime("%H") + ":" + i.strftime("%M")
             nome_apertura = " ".join(params)  #per concatenare nome e cognome
             bot.sendMessage(chat_id, 'Ok! {} ho aperto l\'ufficio'.format(nome_apertura))
             stato_apertura = 0
           else:
            bot.sendMessage(chat_id, 'Mi spiace, non capisco\nUsa /help per sapere cosa posso fare!')


def on_callback_query(msg):
    query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
    chat_id = msg['from']['id']
    #query_data contiene il valore callback_data del pulsante premuto
    
    if query_data.startswith('calendar-day-'):
       saved_date = current_shown_dates.get(chat_id)
       if(saved_date is not None):
         day=query_data[13:]
         date = datetime.date(int(saved_date[0]),int(saved_date[1]),int(day))
         start_date = str(date) + "T00:00:00."+datetime.datetime.now().strftime("%S")+'Z'
         end_date = str(date) + "T23:59:59."+datetime.datetime.now().strftime("%S")+'Z'
         message = search_calendar(start_date, end_date)
         bot.sendMessage(chat_id, message, parse_mode = 'Markdown')
       else:
         bot.sendMessage (chat_id, "Errore! Per favore riprova")
        
          
    elif query_data.startswith('next-month'):
        saved_date = current_shown_dates.get(chat_id)
        if(saved_date is not None):
         year,month = saved_date
         month+=1
         if month>12:
            month=1
            year+=1
         date = (year,month)
         current_shown_dates[chat_id] = date
         keyboard= create_calendar(year,month)
         #Non viene creata una nuova keyboard con il nuovo mese ma viene aggiornata quella già esistente
         bot.editMessageReplyMarkup(telepot.message_identifier(msg['message']), reply_markup = keyboard)
        else:
           bot.sendMessage (chat_id, "Errore! Per favore riprova") 
        
    elif query_data.startswith('previous-month'):
        saved_date = current_shown_dates.get(chat_id)
        if(saved_date is not None):
         year,month = saved_date
         month-=1
         if month<1:
            month=12
            year-=1
         date = (year,month)
         current_shown_dates[chat_id] = date
         keyboard= create_calendar(year,month)
         bot.editMessageReplyMarkup(telepot.message_identifier(msg['message']), reply_markup = keyboard)
        else:
            bot.sendMessage (chat_id, "Errore! Per favore riprova")
        
    
bot = telepot.Bot(TOKEN)  #per accedere alle API di telegram
bot.message_loop({'chat': on_chat_message,
                  'callback_query': on_callback_query})  #loop che resta in ascolta di un nuovo messaggio
                                                         #handler -> on_chat_message per i messaggi testuali (comandi)
                                                         #        -> on_callback_query per i pulsanti della Inline Keyboard

 
while 1:
    time.sleep(5)

