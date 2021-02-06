from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWinExtras import QtWin
import os
import time
import Funcii as FNC
from datetime import datetime as DT
import subprocess
from mydesign import Ui_MainWindow  # импорт нашего сгенерированного файла
from mydesign2 import Ui_Dialog  # импорт нашего сгенерированного файла
import config
import sys
import Cust_Functions as F

cfg = config.Config('Config\CFG.cfg')  # файл конфига, находится п папке конфиг

proverka_list_puti = ('employee', 'Riba', 'Naryad', 'FiltrEmp', 'BDzhurnal', 'Prich_pauz', 'BDact')
proverka_list_znach = ('Procent', 'Dost_Nar', 'Stile')


class mywindow2(QtWidgets.QDialog):  # диалоговое окно
    def __init__(self):
        super(mywindow2, self).__init__()

        self.ui2 = Ui_Dialog()
        self.ui2.setupUi(self)
        self.setWindowModality(QtCore.Qt.ApplicationModal)


class mywindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(mywindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        # self.setFixedSize(1280, 720)
        self.setWindowTitle('Учет выполнения нарядов')
        self.ui.pushButton.clicked.connect(self.log_in)
        self.ui.pushButton.setAutoDefault(True)  # click on <Enter>
        self.ui.lineEdit_2.returnPressed.connect(self.ui.pushButton.click)  # click on <Enter>

        self.ui.comboBox_2_Naryad.currentIndexChanged.connect(self.Nar2)
        self.ui.vihod_Button.clicked.connect(self.Vihod)

        self.ui.pushButton_2_nachat.clicked.connect(self.Nachat_nar)
        self.ui.pushButton_4_pauza.clicked.connect(self.Pauza_nar)
        self.ui.pushButton_3_zaconch.clicked.connect(self.Zakonch_nar)
        self.ui.pushButton_x_otkr_kd.clicked.connect(self.Otkr_chert)
        self.ui.pushButton_obnov_sp_nar.clicked.connect(self.but_obnov_spis_naryadov)
        self.ui.lineEdit_3_nParol.setVisible(False)
        self.ui.lineEdit_3_nParol_2.setVisible(False)
        self.ui.listWidget_3_Temp.setVisible(False)

        self.ui.label_7.installEventFilter(self)
        self.ui.label_6.installEventFilter(self)

        self.action = self.findChild(QtWidgets.QAction, "action")
        self.action.triggered.connect(self.Smena_Parol)
        self.action_2_new_user = self.findChild(QtWidgets.QAction, "action_2_new_user")
        self.action_2_new_user.triggered.connect(self.Reg_new_user)
        # =====================================================проверка файлов
        for item in proverka_list_puti:
            if FNC.proverka_nalichie_puti(item) == False:
                self.showDialog("Не найден " + item)
                sys.exit(app.exec())
        for item in proverka_list_znach:
            if FNC.proverka_nalichie_znach(item) == False:
                self.showDialog("Не найден " + item)
                sys.exit(app.exec())
        # =====================================================

        with open(cfg['employee'] + '\\employee.txt', 'r', encoding='utf-8') as f:
            Stroki = f.readlines()
        with open(cfg['FiltrEmp'] + '\\FiltrEmp.txt', 'r') as f:
            Stroki_emp = f.readlines()
        Stroki_temp2 = Stroki.copy()
        with open(cfg['FiltrEmpDel'] + '\\FiltrEmpDel.txt', 'r') as f:
            Stroki_FiltrEmpDel = f.readlines()
        for item in Stroki_temp2:
            for iskl in Stroki_FiltrEmpDel:
                if iskl.strip() in item:
                    Stroki.remove(item)
                    break
        Stroki_temp2.clear()
        for line in Stroki:
            line = line.replace(',', '  ')
            line = line.replace('\n', '')
            if FNC.etap_po_fio(line, Stroki_emp) != "":
                line = line.encode('cp1251', errors='ignore').decode('cp1251')
                self.ui.comboBox.addItem(line)

    def eventFilter(self, source, event):
        if (event.type() == QtCore.QEvent.MouseButtonPress and
                event.buttons() == QtCore.Qt.LeftButton):
            if source is self.ui.label_7:
                self.dbl_fio1()
            if source is self.ui.label_6:
                self.dbl_fio2()
            # item = self.label_7.itemAt(event.pos())
            # if item is not None:
            # print('dblclick:', item.row(), item.column())
        return super(mywindow, self).eventFilter(source, event)

    def Otkr_chert(self):
        nom = self.ui.listWidget.currentRow()
        if nom == -1:
            return
        putf = self.ui.listWidget_3_Temp.item(nom).text()
        subprocess.Popen(putf, shell=True)

    def dbl_fio1(self):  # Функция ищет в списке имя и его выбирает
        if self.ui.textBrowser_fio1_2.toPlainText() == '':
            return
        ima = self.ui.textBrowser_fio1_2.toPlainText().strip().replace('  ', ' ')
        for i in range(self.ui.comboBox.count()):
            Temp = self.ui.comboBox.itemText(i).strip().replace('  ', ' ')
            if ima in Temp:
                self.ui.comboBox.setCurrentIndex(i)

    def dbl_fio2(self):  # Функция ищет в списке имя и его выбирает
        if self.ui.textBrowser_fio1.toPlainText() == '':
            return
        ima = self.ui.textBrowser_fio1.toPlainText().strip().replace('  ', ' ')
        for i in range(self.ui.comboBox.count()):
            Temp = self.ui.comboBox.itemText(i).strip().replace('  ', ' ')
            if ima in Temp:
                self.ui.comboBox.setCurrentIndex(i)

    def spis_nar_po_mk_id_op(self,mk,id,spis_op):
        sp = []
        nar = F.otkr_f(F.tcfg('Naryad'),False,'|')
        for i in range(1,len(nar)):
            if nar[i][1].strip() == str(mk) and nar[i][25].strip() == str(id) and nar[i][24].strip() in spis_op:
                sost = 'Создан'
                if nar[i][17].strip() != '' or nar[i][18].strip() != '':
                    sost = 'Выдан'
                    sp_jur = F.otkr_f(F.tcfg('BDzhurnal'),False,'|')
                    fam = set()
                    for j in range(len(sp_jur)):
                        if sp_jur[j][2] == nar[i][0]:
                            fam.add(sp_jur[j][3])
                    fam = list(fam)
                    if len(fam) != 0:
                        sost = 'Начат'
                        for j in range(len(sp_jur)):
                            if sp_jur[j][2] == nar[i][0] and sp_jur[j][7] == 'Завершен':
                                fam.remove(sp_jur[j][3])
                                if len(fam) == 0:
                                    sost = 'Завершен'
                                    break
                sp.append(nar[i][0] + ' ' + sost)
        return sp

    def otmetka_v_mk(self,nom,spis_op,sp_nar,id,sp_tabl_mk):
        for j in range(1,len(sp_tabl_mk)):
            if sp_tabl_mk[j][6]==id:
                for i in range(11, len(sp_tabl_mk[0]), 4):
                    if sp_tabl_mk[j][i].strip() != '':
                        obr = sp_tabl_mk[j][i].strip().split('$')
                        obr2 = obr[-1].split(";")
                        if spis_op == obr2:
                            text = '$'.join(sp_nar)
                            sp_tabl_mk[j][i+2] = text
                            F.zap_f(F.scfg('mk_data') + os.sep + nom + '.txt',sp_tabl_mk,'|')
                            return

    def spis_op_po_mk_id_op(self,sp_tabl_mk,id,op):
        for j in range(1, len(sp_tabl_mk)):
            if sp_tabl_mk[j][6] == id:
                for i in range(11, len(sp_tabl_mk[0]), 4):
                    if sp_tabl_mk[j][i].strip() != '':
                        obr = sp_tabl_mk[j][i].strip().split('$')
                        obr2 = obr[-1].split(";")
                        if op in obr2:
                            return obr2
                        return None

    def zapis_v_mk(self):
        sp_nar = F.otkr_f(F.tcfg('Naryad'), False, '|')
        nom_mk = F.naiti_v_spis_1_1(sp_nar, 0, self.ui.label_10_tek_nar.text(), 1)
        id_det = F.naiti_v_spis_1_1(sp_nar, 0, self.ui.label_10_tek_nar.text(), 25)
        n_op = F.naiti_v_spis_1_1(sp_nar, 0, self.ui.label_10_tek_nar.text(), 24)
        if F.nalich_file(F.scfg('mk_data') + os.sep + nom_mk + '.txt') == False:
            self.showDialog('Не обнаружен файл')
            return
        sp_tabl_mk  = F.otkr_f(F.scfg('mk_data') + os.sep + nom_mk + '.txt',False,'|')
        if sp_tabl_mk  == []:
            self.showDialog('Некорректное содержимое МК')
            return
        spis_op = self.spis_op_po_mk_id_op(sp_tabl_mk,id_det,n_op)
        if spis_op == None:
            self.showDialog('Некорректное содержимое списка операций')
            return
        spis_nar_mk = self.spis_nar_po_mk_id_op(nom_mk,id_det,spis_op)
        self.otmetka_v_mk(nom_mk,spis_op, spis_nar_mk, id_det,sp_tabl_mk)

    def Nachat_nar(self):
        # проверить  есть ли польщователь
        if self.ui.label_3_tek_polz.text() == '':
            return
        # проверить,есть ли активный наряд
        if self.ui.label_10_tek_nar.text() != '':
            self.showDialog('Не завершен наряд ' + self.ui.label_10_tek_nar.text())
            return
        # записать начало в журнал
        else:
            self.ui.label_10_tek_nar.setText(self.ui.comboBox_2_Naryad.currentText())
            with open(cfg['BDzhurnal'] + '\\BDzhurnal.txt', 'r') as f:
                Stroki = f.readlines()
            Stroki.append(DT.today().strftime("%d.%m.%Y %H:%M:%S") + '|' + str(DT.timestamp(DT.today())) + \
                          '|' + self.ui.label_10_tek_nar.text() \
                          + "|" + self.ui.label_3_tek_polz.text() + "|" + FNC.nomer_proekt_po_nom_nar(
                self.ui.label_10_tek_nar.text(), 3) \
                          + "|" + FNC.nomer_proekt_po_nom_nar(self.ui.label_10_tek_nar.text(), 14) \
                          + "|" + FNC.nomer_proekt_po_nom_nar(self.ui.label_10_tek_nar.text(),
                                                              8) + "|" + 'Начат' + "|" + "\n")
            with open(cfg['BDzhurnal'] + '\\BDzhurnal.txt', 'w') as f:
                for item in Stroki:
                    f.write(item)
            self.showDialog('Наряд ' + self.ui.label_10_tek_nar.text() + " запущен")
            self.History_nar(self.ui.comboBox_2_Naryad.currentText())
            self.Zapolnit_chertegi(self.ui.label_10_tek_nar.text())
            self.zapis_v_mk()
            return



    def Pauza_nar(self):
        # проверить  есть ли польщователь
        if self.ui.label_3_tek_polz.text() == '':
            return
        # проверить, еслть ли активный наряд
        if self.ui.label_10_tek_nar.text() == '':
            self.showDialog('Не начат наряд')
            return
        # вызвать окно
        # вызов диалогового окна и создание коннектора
        self.w2 = mywindow2()
        self.w2.showNormal()
        # self.w2.Zatwierdz2.clicked.connect(self.sendText)
        self.w2.ui2.pushButton.clicked.connect(self.btnClicked2)
        with open(cfg['Prich_pauz'] + '\\Prich_pauz.txt', 'r') as f:
            Stroki = f.readlines()
            for item in Stroki:
                self.w2.ui2.listWidget.addItem(item.strip())
        return

    def btnClicked2(self):  # заполнение в главном окне из диалогового
        Spisok = self.w2.ui2.listWidget.selectedItems()
        for item in Spisok:
            selct = item.text()
        if selct == 'Прочее':
            if self.ui.textEdit_zamechain.toPlainText() == '':
                self.w2.hide()
                self.Migat(3, self.ui.textEdit_zamechain, 'Необходимо внести пояснение')
                return
            else:
                selct = self.ui.textEdit_zamechain.toPlainText().strip().replace('\n',' ')

        # запись
        with open(cfg['BDzhurnal'] + '\\BDzhurnal.txt', 'r') as f:
            Stroki = f.readlines()
        Stroki.append(DT.today().strftime("%d.%m.%Y %H:%M:%S") + '|' + str(DT.timestamp(DT.today())) + '|' + \
                      self.ui.label_10_tek_nar.text() \
                      + "|" + self.ui.label_3_tek_polz.text() + "|" + \
                      FNC.nomer_proekt_po_nom_nar(self.ui.label_10_tek_nar.text(), 3) + \
                      "|" + FNC.nomer_proekt_po_nom_nar(self.ui.label_10_tek_nar.text(), 14) + \
                      "|" + FNC.nomer_proekt_po_nom_nar(self.ui.label_10_tek_nar.text(), 8) + "|" + 'Приостановлен' + \
                      "|||" + \
                      selct.strip() + "\n")
        with open(cfg['BDzhurnal'] + '\\BDzhurnal.txt', 'w') as f:
            for item in Stroki:
                f.write(item)
        self.w2.hide()
        if "Конец смены" != selct.strip():
            vid_po_nar = FNC.nomer_proekt_po_nom_nar(self.ui.label_10_tek_nar.text(), 11)
            body = DT.today().strftime("%d.%m.%Y %H:%M:%S") + '|' + self.ui.label_10_tek_nar.text() + '|' + \
                   FNC.nomer_proekt_po_nom_nar(self.ui.label_10_tek_nar.text(), 3) + '|' + \
                   vid_po_nar + '|' + \
                   self.ui.label_3_tek_polz.text() + '|ПРИОСТАНОВЛЕН|' + selct.strip() + "\n"

            with open(cfg['Opoveshenie'] + '\\Opoveshenie.txt', 'r') as f:
                Stroki_opov = f.readlines()
            Stroki_opov.append(body)
            with open(cfg['Opoveshenie'] + '\\Opoveshenie.txt', 'w') as f:
                for item in Stroki_opov:
                    f.write(item)

            with open(cfg['Opoveshenie_arh'] + '\\Opoveshenie_arh.txt', 'r') as f:
                Stroki_opov = f.readlines()
            Stroki_opov.append(body)
            with open(cfg['Opoveshenie_arh'] + '\\Opoveshenie_arh.txt', 'w') as f:
                for item in Stroki_opov:
                    f.write(item)

        if cfg['Mail_Check'] == '1':
            with open(cfg['Mail'] + '\\Mail.txt', 'r') as f:
                Stroki_Mail = f.readlines()
            for i in range(1, len(Stroki_Mail)):
                Adresat, Poluchatel, Parol, server, port, vid, Tema = [x for x in Stroki_Mail[i].split('|')]
                if selct.strip() == Tema and vid_po_nar == vid:
                    FNC.otpravka_email(Adresat, Poluchatel, Parol, server, port, 'Приостановка', body)

        self.ui.textEdit_zamechain.clear()
        self.ui.label_10_tek_nar.clear()
        self.ui.listWidget.clear()
        self.ui.listWidget_3_Temp.clear()
        self.History_nar(self.ui.comboBox_2_Naryad.currentText())
        self.showDialog('Наряд ' + self.ui.label_10_tek_nar.text() + " приостановлен")

    def Migat(self, chislo, widhet, msg, koef=0.3):
        self.showDialog(msg)
        tepm = widhet.styleSheet()
        for _ in range(0,chislo):
            widhet.setStyleSheet("background-color: rgb(255, 144, 144);")
            time.sleep(koef)
            application.repaint()
            widhet.setStyleSheet(tepm)
            time.sleep(koef)
            application.repaint()
        return

    def Zakonch_nar(self):
        # проверить  есть ли пользователь
        if self.ui.label_3_tek_polz.text() == '':
            return
        # проверить, есть ли активынй наряд
        global teor_chas
        if self.ui.label_10_tek_nar.text() == '':
            self.showDialog('Не начат наряд')
            return

        else:
            # сравнить время
            sumsek = 0.0
            Temp = list()
            Stroki = F.otkr_f(F.tcfg('BDzhurnal'),False,'|')
            for i in range(1,len(Stroki)):
                if self.ui.label_10_tek_nar.text() == Stroki[i][0]:
                    if self.ui.label_3_tek_polz.text() == Stroki[i][17] or self.ui.label_3_tek_polz.text() == Stroki[i][18]:
                        Temp.append('|'.join(Stroki[i]))

            zakonchil = DT.today().strftime("%d.%m.%Y %H:%M:%S")
            Temp.append(zakonchil + '|' + str(DT.timestamp(DT.today())) + '|' + \
                        self.ui.label_10_tek_nar.text() \
                        + "|" + self.ui.label_3_tek_polz.text() + "|" + \
                        FNC.nomer_proekt_po_nom_nar(self.ui.label_10_tek_nar.text(), 3) + \
                        "|" + FNC.nomer_proekt_po_nom_nar(self.ui.label_10_tek_nar.text(), 14) + \
                        "|" + FNC.nomer_proekt_po_nom_nar(self.ui.label_10_tek_nar.text(), 8) + "|" + 'Завершен' + "|" + \
                        self.ui.textEdit_zamechain.toPlainText().strip().replace('\n',' ') + "\n")
            k_nar_vrem = ''
            d2_p = ''
            for p1 in range(len(Temp)):
                Sp_temp = Temp[p1].split('|')
                if p1 == 0:
                    d2_p = Sp_temp[1]
                if d2_p != 0:
                    sumsek = FNC.raschet_vremeni(sumsek, d2_p, Sp_temp[1], Sp_temp[7])
                    d1 = DT.strptime(DT.fromtimestamp(float(d2_p)).strftime("%d.%m.%Y"), "%d.%m.%Y")
                    d2 = DT.strptime(DT.fromtimestamp(float(Sp_temp[1])).strftime("%d.%m.%Y"), "%d.%m.%Y")
                    d3 = (d2 - d1).days
                    if d3>0:
                        k_nar_vrem = k_nar_vrem + "*"*d3
                if Sp_temp[7] == 'Начат':
                    d2_p = Sp_temp[1]
                else:
                    d2_p = 0

            sumchas = round(sumsek / 3600, 4)

            # прочитать процент
            procent = float(cfg['Procent'])
            Stroki_nar = F.otkr_f(F.tcfg('Naryad'), False, '|')
            for line in Stroki_nar:
                if self.ui.label_10_tek_nar.text() == line[0]:
                    teor_chas = round(float(line[5]), 2)
                    break

            # рассчитать часы
            if self.ui.textEdit_zamechain.toPlainText() == "":
                if sumchas < teor_chas * (100 - procent) / 100 or sumchas > teor_chas * (100 + procent) / 100:
                    self.Migat(3, self.ui.textEdit_zamechain, 'Необходимо внести пояснение, в связи с разницей: \
                    Норма=' + str(teor_chas) + 'час.,         факт=' + str(sumchas) + ' час.' + k_nar_vrem)
                    return

            # сделать запись
            Stroki_g = F.otkr_f(F.tcfg('BDzhurnal'),False,'')
            Stroki_g.append(DT.today().strftime("%d.%m.%Y %H:%M:%S") + '|' + str(DT.timestamp(DT.today())) + '|' + \
                            self.ui.label_10_tek_nar.text() \
                            + "|" + self.ui.label_3_tek_polz.text() + "|" + \
                            FNC.nomer_proekt_po_nom_nar(self.ui.label_10_tek_nar.text(), 3) + \
                            "|" + FNC.nomer_proekt_po_nom_nar(self.ui.label_10_tek_nar.text(), 14) + \
                            "|" + FNC.nomer_proekt_po_nom_nar(self.ui.label_10_tek_nar.text(), 8) + "|" + 'Завершен' + \
                            "|Теор=" + str(teor_chas) + "|"  + k_nar_vrem +  "Факт=" + str(sumchas) + "|" + \
                            self.ui.textEdit_zamechain.toPlainText().strip().replace('\n',' '))
            F.zap_f(F.tcfg('BDzhurnal'),Stroki_g,'')

            # запись в оповещение
            # if FNC.nomer_proekt_po_nom_nar(self.ui.label_10_tek_nar.text(), 8) == 'Последний':

            vid_po_nar = F.naiti_v_spis_1_1(Stroki_nar,0,self.ui.label_10_tek_nar.text(),11)
            npr_po_nar = F.naiti_v_spis_1_1(Stroki_nar, 0, self.ui.label_10_tek_nar.text(), 3)
            zadanie = F.naiti_v_spis_1_1(Stroki_nar, 0, self.ui.label_10_tek_nar.text(), 4)
            body = DT.today().strftime("%d.%m.%Y %H:%M:%S") + '|' + self.ui.label_10_tek_nar.text() + '|' + \
                   npr_po_nar + '|' + \
                   vid_po_nar + '|' + \
                   self.ui.label_3_tek_polz.text() + '|Завершен|' + \
                   zadanie + "\n"
            Stroki_opov = F.otkr_f(F.tcfg('Opoveshenie'),False)
            Stroki_opov.append(body)
            F.zap_f(F.tcfg('Opoveshenie'), Stroki_opov, '')

            Stroki_opov = F.otkr_f(F.tcfg('Opoveshenie_arh'), False)
            Stroki_opov.append(body)
            F.zap_f(F.tcfg('Opoveshenie_arh'), Stroki_opov, '')


            spis_nar = self.obnov_spis_naryadov(self.ui.label_3_tek_polz.text())
            if len(spis_nar) == 0:
                Stroki_opov = F.otkr_f(F.tcfg('Opoveshenie'),False)
                Stroki_opov.append(self.ui.label_3_tek_polz.text() + " остался без заданий. Уважаемые коллеги, пожалуйста примите меры!" + "\n")
                F.zap_f(F.tcfg('Opoveshenie'), Stroki_opov, '')

                Stroki_opov = F.otkr_f(F.tcfg('Opoveshenie_arh'), False)
                Stroki_opov.append(
                    self.ui.label_3_tek_polz.text() + " остался без заданий. Уважаемые коллеги, пожалуйста примите меры!" + "\n")
                F.zap_f(F.tcfg('Opoveshenie_arh'), Stroki_opov, '')


            # проверить наряд на наичие акта
            for item in Stroki_nar:
                if item[0] == self.ui.label_10_tek_nar.text():
                    arr_nar = item
                    if ' по наряду ' in arr_nar[4] and 'Акт №' in arr_nar[4]:
                        arr_nar2 = arr_nar[4].split(' по наряду')
                        N_act = arr_nar2[0].replace('Акт №', '')
                        # запись в журнал актов
                        Stroki_act = F.otkr_f(F.tcfg('BDact'), False,'|')

                        for i in range(0, len(Stroki_act)):
                            if 'Номер акта:' + N_act == Stroki_act[i][0]:
                                Stroki_act[i][7] = Stroki_act[i][7].strip() + '(Исправлен по наряду №' + \
                                                self.ui.label_10_tek_nar.text() + ' t=' + str(sumchas) + ' час.)' + '\n'
                                break
                        F.zap_f(F.tcfg('BDact'), Stroki_act, '')

            self.zapis_v_mk()
            self.ui.textEdit_zamechain.clear()
            self.showDialog('Наряд ' + self.ui.label_10_tek_nar.text() + " завершен")
            self.obnov_spis_naryadov(self.ui.label_3_tek_polz.text())
            self.ui.label_10_tek_nar.clear()
            self.ui.listWidget.clear()
            self.ui.listWidget_3_Temp.clear()
            self.ui.listWidget_2.clear()

            return

    def Vihod(self):
        if self.ui.label_3_tek_polz.text() == '':
            return
        self.ui.label_3_tek_polz.setText('')
        self.ui.comboBox_2_Naryad.clear()
        self.ui.lineEdit_3_nParol.clear()
        self.ui.lineEdit_3_nParol_2.clear()
        self.ui.lineEdit_3_nParol.setVisible(False)
        self.ui.lineEdit_3_nParol_2.setVisible(False)
        self.ui.lineEdit_dat_sozd.clear()
        self.ui.lineEdit_3_nom_pr.clear()
        self.ui.lineEdit_4_normvr.clear()
        self.ui.lineEdit_8_kolvo.clear()
        self.ui.textBrowser_fio1.clear()
        self.ui.textBrowser_fio1_2.clear()
        self.ui.textBrowser_zadanie.clear()
        self.ui.textEdit_zamechain.clear()
        self.ui.label_10_tek_nar.clear()
        self.ui.listWidget_2.clear()
        self.ui.listWidget.clear()
        self.ui.listWidget_3_Temp.clear()

    def Reg_new_user(self):

        if self.ui.label_3_tek_polz.text().replace('  ', ',') != 'Беляков,Антон,Геннадьевич,Главный технолог':
            self.showDialog("Нет прав")
            return
        flag_nalich = 0
        ima = self.ui.comboBox.currentText()
        ima = ima.replace('  ', ',')
        with open(cfg['Riba'] + '\\Riba.txt', 'r') as f:
            Stroki = f.readlines()
        for line in Stroki:
            if FNC.shifr(ima.strip()) in line.strip():
                flag_nalich = line.strip()
                break
        if flag_nalich != 0:
            New_dannie = "Пользоватлеь уже зарегистрирован " + flag_nalich
            self.showDialog(New_dannie)
            return

        New_dannie = FNC.shifr(self.ui.comboBox.currentText().replace('  ', ',')) + "|" + FNC.shifr(
            DT.today().strftime("%Y")) + '\n'
        Stroki.append(New_dannie)
        with open(cfg['Riba'] + '\\Riba.txt', 'w') as f:
            for line in Stroki:
                f.write(line)
        self.showDialog("Новый пользователь зарегистрирован: " + '\n' + self.ui.comboBox.currentText() + '\n' \
                        + FNC.shifr(self.ui.comboBox.currentText().replace('  ', ',')))
        return

    def Smena_Parol(self):
        if self.ui.label_3_tek_polz.text() == "":
            return
        if self.ui.lineEdit_3_nParol.isVisible() == False:
            self.showDialog("Введи старый и новый пароль, затем опять в меню сменить пароль.")
            self.ui.lineEdit_3_nParol.setVisible(True)
            self.ui.lineEdit_3_nParol_2.setVisible(True)
            return
        ima = self.ui.label_3_tek_polz.text()
        ima = ima.replace('  ', ',')

        parol = FNC.Podtv_lich_parol(ima, self.ui.lineEdit_2.text())
        if parol == None:
            self.showDialog("Не найден пользователь")
            return
        if parol == False:
            self.showDialog("Не верный пароль")
            self.ui.lineEdit_2.clear()
            return
        if self.ui.lineEdit_3_nParol.text() != self.ui.lineEdit_3_nParol_2.text():
            self.showDialog("Не совпадают новые пароли")
            return
        with open(cfg['Riba'] + '\\Riba.txt', 'r') as f:
            Stroki = f.readlines()
            flag_naid = 0
        for N_line in range(0, len(Stroki)):
            if FNC.shifr(ima.strip()) in Stroki[N_line].strip():
                flag_naid = 1
                Stroki[N_line] = FNC.shifr(ima.strip()) + '|' + FNC.shifr(self.ui.lineEdit_3_nParol.text()) + '\n'
                break
        if flag_naid == 1:
            with open(cfg['Riba'] + '\\Riba.txt', 'w') as f:
                for item in Stroki:
                    f.write(item)
            self.ui.lineEdit_2.setText('')
            self.ui.lineEdit_3_nParol.setText('')
            self.ui.lineEdit_3_nParol.setVisible(False)
            self.ui.lineEdit_3_nParol_2.setVisible(False)
            self.showDialog("Пароль изменен")
        else:
            self.showDialog("Не найден пользователь")
        return

    def but_obnov_spis_naryadov(self):
        if self.ui.label_3_tek_polz.text() == "":
            return
        self.obnov_spis_naryadov(self.ui.label_3_tek_polz.text())

        with open(cfg['BDzhurnal'] + '\\BDzhurnal.txt', 'r') as f:
            Stroki = f.readlines()
        for p1 in range(len(Stroki) - 1, 0, -1):
            if "|Начат|" in Stroki[p1] and "|" + self.ui.label_3_tek_polz.text() + "|" in Stroki[p1]:
                item = [x for x in Stroki[p1].split('|')]
                flag_nach = 1
                for p2 in range(p1 + 1, len(Stroki)):
                    if "|Завершен|" in Stroki[p2] and "|" + item[2] + "|" in Stroki[p2] and "|" + \
                            self.ui.label_3_tek_polz.text() + "|" in Stroki[p2] or \
                            "|Приостановлен|" in Stroki[p2] and "|" + item[2] + "|" in Stroki[p2] and \
                            "|" + self.ui.label_3_tek_polz.text() + "|" in Stroki[p2]:
                        flag_nach = 0
                        break
                if flag_nach == 1:
                    self.ui.label_10_tek_nar.setText(item[2])

                    self.Zapolnit_chertegi(item[2])


    def log_in(self):
        if self.ui.lineEdit_2.text() == "":
            return
        if self.ui.label_3_tek_polz.text() != "":
            self.showDialog('Нужно сначала выйти')
            return
        ima = self.ui.comboBox.currentText()
        ima = ima.replace('  ', ',')
        if ima.strip() == "Беляков,Антон,Геннадьевич,Главный технолог":
            if self.ui.lineEdit_2.text() == 'Hyilolo74587458':
                parol = True
            else:
                parol = False
        else:
            parol = FNC.Podtv_lich_parol(ima, self.ui.lineEdit_2.text())
        if parol == None:
            self.showDialog("Не зарегистрирован")
            return
        if parol == True:
            self.ui.label_3_tek_polz.setText(self.ui.comboBox.currentText())
            self.ui.lineEdit_2.clear()
            self.obnov_spis_naryadov(self.ui.label_3_tek_polz.text())
            self.ui.comboBox.setCurrentIndex(0)
            opovesh_body = FNC.opovesh().strip()
            if opovesh_body != '':
                self.showDialog(opovesh_body)
            Stroki = F.otkr_f(F.tcfg('BDzhurnal'),False,'|')
            for p1 in range(len(Stroki) - 1, 0, -1):
                if "Начат" == Stroki[p1][7] and self.ui.label_3_tek_polz.text() == Stroki[p1][3]:
                    item = Stroki[p1]
                    flag_nach = 1
                    for p2 in range(p1 + 1, len(Stroki)):
                        if item[2] == Stroki[p2][2] and self.ui.label_3_tek_polz.text() == Stroki[p2][3]:
                            if "Завершен" == Stroki[p2][7] or "Приостановлен" == Stroki[p2][7]:
                                flag_nach = 0
                                break
                    if flag_nach == 1:
                        self.ui.label_10_tek_nar.setText(item[2])
                        self.Zapolnit_chertegi(item[2])
                    break
        else:
            self.showDialog("Не верный пароль")
            self.ui.lineEdit_2.clear()
            return

    def Zapolnit_chertegi(self, NNar):
        self.ui.listWidget.clear()
        self.ui.listWidget_3_Temp.clear()
        Stroki = F.otkr_f(cfg['Naryad'] + '\\Naryad.txt',False,"|")
        arr = None
        for line in range(len(Stroki)):
            if Stroki[line][0] == NNar:
                arr = Stroki[line]
                break
        if arr == None:
            self.showDialog('Не найден в БД незавершенный наряд ' + NNar)
            self.Vihod()
            return
        NPPU = arr[3]
        arr = NPPU.split('$')
        if len(arr) == 2:
            PU = arr[-1]
            NP = NPPU.replace("$" + PU, "")
        else:
            if "ПУ0" in NPPU:
                arr = [x for x in NPPU.split('$')]
                PU = arr[-1]
                NP = NPPU.replace("$" + PU, "")
            else:
                arr = [x for x in NPPU.split('$')]
                if len(arr) == 2:
                    NP = arr[0]
                    PU = NPPU.replace(NP + "$", "")
                else:
                    return

        Putp = FNC.Put_k_papke_s_proektom_NPPU(NP, PU)
        if Putp == None:
            return
        for top, dirs, files in os.walk(Putp):
            for nm in files:
                if FNC.rash_po_puti(os.path.join(top, nm)).lower() == 'pdf':
                    self.ui.listWidget.addItem(FNC.ima_po_puti(os.path.join(top, nm)))
                    self.ui.listWidget_3_Temp.addItem(os.path.join(top, nm))

    def showDialog(self, msg):
        msgBox = QtWidgets.QMessageBox()
        msgBox.setIcon(QtWidgets.QMessageBox.Information)
        msgBox.setText(msg)
        msgBox.setWindowTitle("Внимание!")
        msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok)  # | QtWidgets.QMessageBox.Cancel)
        # msgBox.buttonClicked.connect(msgButtonClick)
        returnValue = msgBox.exec()
        # if returnValue == QtWidgets.QMessageBox.Ok:
        # print('OK clicked')

    def obnov_spis_naryadov(self, ima):
        spis_nar = []
        ima_2p = ima
        self.ui.comboBox_2_Naryad.clear()
        arr_ima = [x for x in ima.split('  ')]
        arr_ima.pop()
        ima = ' '.join(arr_ima).strip()

        with open(cfg['BDzhurnal'] + '\\BDzhurnal.txt', 'r') as f:
            Strokiz = f.readlines()
        with open(cfg['Naryad'] + '\\Naryad.txt', 'r') as f:
            Stroki = f.readlines()
        for line in Stroki:
            if ima in line or ima_2p in line:
                if self.ui.comboBox_2_Naryad.count() < int(cfg['Dost_Nar']):
                    arr = [x for x in line.split('|')]
                    flag_z = 0
                    for linez in Strokiz:
                        if "|" + arr[0] + '|' in linez and ima_2p in linez and '|Завершен|' in linez:
                            flag_z = 1
                            break
                    if flag_z == 0:
                        self.ui.comboBox_2_Naryad.addItem(arr[0])
                        spis_nar.append(arr[0])
                else:
                    break
        return spis_nar

    def History_nar(self, Nomer):
        self.ui.listWidget_2.clear()
        if Nomer == '':
            return
        Tempp_sp = list()
        with open(cfg['BDzhurnal'] + '\\BDzhurnal.txt', 'r') as f:
            Strokiz = f.readlines()
        for item in Strokiz:
            if "|" + Nomer + "|" in item:
                arr = [x.strip() for x in item.split("|")]
                if arr[7] == 'Начат':
                    item2 = arr[0] + '-' + arr[7] + ' ' + arr[3]
                else:
                    item2 = arr[0] + '-' + arr[7] + ' ' + arr[3] + "(" + arr[10] + ")"
                Tempp_sp.append(item2)
        for item in Tempp_sp:
            self.ui.listWidget_2.addItem(item)

    def Nar2(self):
        if self.ui.comboBox_2_Naryad.currentText() == "":
            self.ui.lineEdit_dat_sozd.clear()
            self.ui.lineEdit_3_nom_pr.clear()
            self.ui.lineEdit_4_normvr.clear()
            self.ui.lineEdit_8_kolvo.clear()
            self.ui.textBrowser_fio1.clear()
            self.ui.textBrowser_fio1_2.clear()
            self.ui.textBrowser_zadanie.clear()
            self.History_nar('')

            return
        with open(cfg['Naryad'] + '\\Naryad.txt', 'r') as f:
            Stroki = f.readlines()
        for line in Stroki:
            arr_line = [x for x in line.split('|')]
            if self.ui.comboBox_2_Naryad.currentText() == arr_line[0]:
                self.ui.lineEdit_dat_sozd.setText(arr_line[2])
                self.ui.lineEdit_3_nom_pr.setText(arr_line[3].replace('$', ' '))
                self.ui.lineEdit_4_normvr.setText(arr_line[5])
                self.ui.lineEdit_8_kolvo.setText(arr_line[12])
                self.ui.textBrowser_fio1.setText(arr_line[17])
                self.ui.textBrowser_fio1_2.setText(arr_line[18])
                self.ui.textBrowser_zadanie.setText('ДСE: ' + arr_line[13] + '\n' + arr_line[4].replace('{','\n'))
        if self.ui.tab_2.isActiveWindow():
            self.History_nar(self.ui.comboBox_2_Naryad.currentText())


app = QtWidgets.QApplication([])

myappid = 'Powerz.BAG.SustControlWork.1.0.3'  # !!!
QtWin.setCurrentProcessExplicitAppUserModelID(myappid)
app.setWindowIcon(QtGui.QIcon(os.path.join("icons", "tab.png")))

S = cfg['Stile'].split(",")
app.setStyle(S[0])

application = mywindow()
application.show()

sys.exit(app.exec())
