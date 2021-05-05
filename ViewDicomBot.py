# -*- coding: utf-8 -*-

from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler, Filters
from telegram import ChatAction
import pydicom as pdm
from PIL import Image
import numpy as np
import os

INPUT_DICOM = 0


def start(update, context):
    update.message.reply_text('Buenas amig@, Este bot te ayudara a leer imagenes medicas DICOM.' \
            ' Usa /dicom para para comenzar procesar el archivo' )

def dicom_command_handler(update, context):
    update.message.reply_text('Enviame el archivo .dcm para enviarte la imagen y alguno de sus datos')
    
    return INPUT_DICOM


def processing_dicom(file):
    
    img = pdm.read_file(file)
    name = img.get('PatientName')
    modality = img.get('Modality')
    obj = img.get('StudyDescription')
    resolution = img.pixel_array.shape
    

    imagen = np.uint8(img.pixel_array)
    res_img = Image.fromarray(imagen, mode="L")
    res_img.save("result.jpg")
    filename = 'result.jpg'
    
    return filename, name, modality, obj, resolution


def send_img(filename,name,modality,obj, resolution, chat):
    
    chat.send_action(action = ChatAction.UPLOAD_PHOTO, timeout = None)
    chat.send_photo(photo = open(filename, 'rb'), 
                    caption = f'Nombre del paciente: {name}\nTipo de estudio medico: {modality}\nTejido analizado: {obj}\nResolucion de la imagen: {resolution}',
                    parse_mode = "HTML")
    
    
def input_dicom(update, context):

    file = update.message.document.get_file()
    name_f = update.message.document.file_name
            
    file.download(name_f)
    filename, name, modality, obj, resolution = processing_dicom(name_f)
    chat = update.message.chat

    send_img(filename, name, modality,obj, resolution, chat)
    os.unlink(name_f)
    os.unlink(filename)  

    return ConversationHandler.END


def main():

    updater = Updater(token = '1741944471:AAGeLIVvmgmZeu0ng-vJxfIdEgQUKC1L3wc', use_context= True)
    dp = updater.dispatcher
    
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(ConversationHandler(
        entry_points = [CommandHandler('dicom', dicom_command_handler)],
        states = {INPUT_DICOM: [MessageHandler(Filters.document, input_dicom)]},
        fallbacks = []))
    
    updater.start_polling()
    updater.idle()
    
    
    
if __name__ == '__main__':
    main()
        