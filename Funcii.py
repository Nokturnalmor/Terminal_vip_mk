import hashlib
import os
import config
import smtplib                                      # Импортируем библиотеку по работе с SMTP
cfg = config.Config('Config\CFG.cfg') #файл конфига, находится п папке конфиг


def opovesh():
    with open(cfg['Opovesh'] + '\\Opovesh.txt', 'r') as f:
        Stroki = f.readlines()
    body = "".join(Stroki)
    return body



def otpravka_email(addr_from,addr_to,password,server,port,Tema,body):


    # Добавляем необходимые подклассы - MIME-типы
    from email.mime.multipart import MIMEMultipart      # Многокомпонентный объект
    from email.mime.text import MIMEText                # Текст/HTML
    #from email.mime.image import MIMEImage              # Изображения

    #addr_from = "from_address@mail.com"                 # Адресат
    #addr_to   = "to_address@mail.com"                   # Получатель
    #password  = "pass"                                  # Пароль

    msg = MIMEMultipart()                               # Создаем сообщение
    msg['From']    = addr_from                          # Адресат
    msg['To']      = addr_to                            # Получатель
    msg['Subject'] = Tema                               # Тема сообщения

    #body = "Текст сообщения"
    msg.attach(MIMEText(body, 'plain'))                 # Добавляем в сообщение текст

    server = smtplib.SMTP(server, port)           # Создаем объект SMTP
    #server.set_debuglevel(True)                         # Включаем режим отладки - если отчет не нужен, строку можно закомментировать
    server.starttls()                                   # Начинаем шифрованный обмен по TLS
    server.login(addr_from, password)                   # Получаем доступ
    server.send_message(msg)                            # Отправляем сообщение
    server.quit()                                       # Выходим







def proverka_nalichie_znach(item):
    if cfg[item] != '':
        return True
    else:
        return False

def proverka_nalichie_puti(item):
    if os.path.exists(cfg[item] + '\\' + item + '.txt') == False:
        return False
    else:
        return True

def shifr(password):
    pass_hash= hashlib.md5(password.encode('utf-8')).hexdigest()
    return pass_hash

def ima_po_puti(putf):
    arr = putf.split('\\')
    return arr[-1]

def rash_po_puti(putf):
    arr = putf.split('\\')
    arr2 = arr[-1].split('.')
    return arr2[-1]

def etap_po_fio(fio,massiv):
    line = fio.replace('\n', '')
    *fio, Dolgn = [x for x in line.split('  ')]
    for item in massiv:
        if Dolgn in item.strip():
            fio, etap = [x for x in item.split('|')]
            return etap.strip()
    return ''

def nomer_proekt_po_nom_nar(nn,kol):
    with open(cfg['Naryad'] + '\\Naryad.txt', 'r') as f:
        Stroki = f.readlines()
    for line in Stroki:
        if line.startswith(nn + '|') == True:
            arr = [x for x in line.split('|')]
            return arr[kol]


def Put_k_papke_s_proektom_NPPU(NP, PU):
    Proekt = NP.strip()
    PU = PU.strip()
    if 'ПУ0' not in PU and PU != "":
        Put_k_pap = cfg['Puti_pr'] + "\\" + PU + "\\" + cfg['Dir_kd'] + "\\"
        if os.path.exists(Put_k_pap) == True:
            return Put_k_pap
    Put_k_pap = cfg['Puti_pr'] + "\\Отдел технолога\\В работе\\20" + Proekt[:2] + "\\" + Proekt + "\\" + PU + "\\" + cfg['Dir_kd'] + "\\"
    if os.path.exists(Put_k_pap) == True:
        return Put_k_pap
    Put_k_pap = cfg['Puti_pr'] + "\\Отдел технолога\\В работе\\20" + Proekt[:2] + "\\" + Proekt + "\\" + cfg['Dir_kd'] + "\\"
    if os.path.exists(Put_k_pap) == True:
        return Put_k_pap
    else:
        print('Не найдена папка для проекта ' + Proekt + ' ' + PU)
    return

def Podtv_lich_parol(FIO,Pred_parol):
    parol = None
    with open(cfg['Riba'] + '\\Riba.txt', 'r') as f:
        Stroki = f.readlines()
    for line in Stroki:
        if shifr(FIO.strip()) in line.strip():
            arr = [x for x in line.split('|')]
            parol = arr[len(arr) - 1]
            parol = parol.replace('\n', '')
            break
    if parol == None:
        return None
    if parol ==shifr(Pred_parol):
        return True
    else:
        return False

def raschet_vremeni(sum_v,shtampN,shtampK,deistv):
    if shtampN == 0:
        return sum_v
    if deistv == 'Начат':
        return sum_v
    if deistv == 'Приостановлен' or deistv == 'Завершен':
        sum_v = float(sum_v) + float(shtampK)- float(shtampN)
        return sum_v


