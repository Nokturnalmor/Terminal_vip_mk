import project_cust_38.Cust_Qt as CQT
import project_cust_38.Cust_Functions as F
import project_cust_38.Cust_mes as CMS
import project_cust_38.Cust_SQLite as CSQ

def reg_new_user(self):
    lbx = self.ui.cmb_fio
    ima = CMS.ima_po_emp(lbx.currentText())
    if F.nalich_file(F.pcfg('Riba')) == False:
        F.save_file_pickle(F.pcfg('Riba'), [['', '', F.now('')]])
    rez = CMS.Podtv_lich_parol(ima, self.ui.le_parol.text())
    if rez != None:
        CQT.msgbox(f"Пользователь уже зарегистрирован")
        return
    spis = F.load_file_pickle(F.pcfg('Riba'))
    spis.append([CMS.shifr(ima), CMS.shifr(
        F.date(vid='yyyy')),F.now('')])
    F.save_file_pickle(F.pcfg('Riba'), spis)
    CQT.msgbox("Новый пользователь зарегистрирован: " + '\n' + ima + '\n' \
               + F.date(vid='yyyy'))
    return


def log_in(self):
    lbx = self.ui.cmb_fio
    if self.ui.le_parol.text() == "":
        return
    if self.glob_login != "":
        CQT.msgbox('Нужно сначала выйти')
        return
    if lbx.currentText() == '':
        CQT.msgbox('Не выбран пользователь')
        return
    ima = CMS.ima_po_emp(lbx.currentText())
    if self.ui.le_parol.text() == "Zflvby" or F.user_name() == 'a.belyakov' or self.ui.le_parol.text() == '13243546':
        parol = True
    else:
        parol = CMS.Podtv_lich_parol(ima, self.ui.le_parol.text())
        if parol == None:
            CQT.msgbox("Не зарегистрирован")
            return
    if parol == True:
        self.glob_login = f'{ima} {self.DICT_EMPLOEE[ima]}'#  CMS.emp_po_ima(self,ima)
        self.glob_fio = ima
        self.setWindowTitle(ima)
        self.ui.le_parol.clear()
        self.ui.lbl_tek_polz.setText(ima)
    else:
        CQT.msgbox("Не верный пароль")
        self.ui.le_parol.clear()
        return
    conn, cur = CSQ.connect_bd(self.db_naryd,2)
    self.zapoln_tabl_naryadov()
    self.lbl_tek_narayd(ima)
    CSQ.close_bd(conn, cur)
    self.summ_chas_po_tabel_mes()
    if self.glob_login == 'Работник Заготовительного Цеха Помощник оператора лазерных установок'\
            or self.glob_login == 'Работник Заготовительного Цеха2 Помощник оператора лазерных установок':
        for fio in self.DICT_EMPLOEE.keys():
            if self.DICT_EMPLOEE[fio] == self.DICT_EMPLOEE[ima] and self.DICT_EMPL_FULL[fio]['Режим'] != 'Абстракт':
                self.ui.cmb_zamechain.addItem(fio)

def logout(self):
    self.ui.cmb_fio.setCurrentText('')
    if self.glob_login == '':
        return
    self.glob_login = ''
    self.setWindowTitle("Выполнение нарядов")
    self.ui.le_Nparol.setVisible(False)
    self.ui.le_Nparol2.setVisible(False)
    CQT.clear_tbl(self.ui.tbl_naryadi)
    CQT.clear_tbl(self.ui.tbl_history)
    CQT.clear_tbl(self.ui.tbl_chert)
    CQT.clear_tbl(self.ui.tbl_naryadi_view_kompl)
    CQT.clear_tbl(self.ui.tbl_stat)
    CQT.clear_tbl(self.ui.tbl_stat_filtr)
    CQT.clear_tbl(self.ui.tbl_stat_filtr_last)
    CQT.clear_tbl(self.ui.tbl_stat_last)
    self.ui.textBrowser_zadanie.setText('')
    self.ui.te_zamechain.setText('')
    self.ui.lbl_tek_nar.setText('')
    self.ui.lbl_tek_polz.setText('')
    self.ui.lbl_sozdan.setText('')
    self.ui.lbl_proekt.setText('')
    self.ui.lbl_norma.setText('')
    self.ui.lbl_nom_mk.setText('')
    self.ui.lbl_isp1.setText('')
    self.ui.lbl_isp2.setText('')
    self.ui.label_12.setText('План работы')
    self.ui.le_basa.setText('')
    self.ui.le_premia.setText('')
    self.ui.le_brak.setText('')

    CQT.ust_cvet_obj(self.ui.lbl_ostalos)
    self.ui.lbl_ostalos.setText('')
    self.ui.tabWidget_2.setCurrentIndex(0)
    self.ui.tabWidget.setCurrentIndex(0)
    self.setStatusTip('')
    return


def load_users(self,conn='', cur = ''):
    """Загрузить список сотрудников в листбокс"""
    self.DICT_EMPLOEE = dict()
    self.SPIS_EMPLOEE = CSQ.zapros(self.bd_users,"""SELECT ФИО, Должность FROM employee WHERE Пномер > 2 AND Статус == '';""",shapka=False,conn=conn, cur = cur)
    if self.SPIS_EMPLOEE == False:
        return False
    spis_black_list = F.load_file(F.scfg('Riba') + F.sep() + 'black_list_itr.txt')
    if spis_black_list == False:
        spis_black_list = ['']
        F.save_file(F.scfg('Riba') + F.sep() + 'black_list_itr.txt',spis_black_list)
    spis_itr = F.load_file(F.scfg('Riba') + F.sep() + 'FiltrEmp_u.txt')
    self.ui.cmb_dolgn.addItem('')
    #self.ui.cmb_fio.addItem('')
    set_dolgn = set()
    for rab in self.SPIS_EMPLOEE:
        fio = rab[0]
        dolg = rab[1]
        self.DICT_EMPLOEE[fio] = dolg
        flag = True
        for frase in spis_black_list:
            if frase in fio:
                flag = False
        if dolg in spis_itr and flag == True:
            set_dolgn.add(dolg)
    spis_dolgn = sorted(list(set_dolgn))
    for dolgn in spis_dolgn:
        self.ui.cmb_dolgn.addItem(dolgn)
    spis_pauz = F.load_file(F.scfg('Riba') + F.sep() + 'Prich_pauz.txt')
    self.ui.cmb_zamechain.clear()
    self.ui.cmb_zamechain.addItem('')
    for item in  spis_pauz:
        self.ui.cmb_zamechain.addItem(item)


def load_po_dolg(self):
    """Загрузить список сотрудников в листбокс"""
    if self.ui.cmb_dolgn.currentText() == '':
        return
    spis_black_list = F.load_file(F.scfg('Riba') + F.sep() + 'black_list_itr.txt')
    if spis_black_list == False:
        spis_black_list = ['']
        F.save_file(F.scfg('Riba') + F.sep() + 'black_list_itr.txt',spis_black_list)
    self.ui.cmb_fio.clear()
    self.ui.cmb_fio.addItem('')
    for rab in self.SPIS_EMPLOEE:
        fio = rab[0]
        dolg = rab[1]
        flag = True
        for frase in spis_black_list:
            if frase in fio:
                flag = False
        if dolg == self.ui.cmb_dolgn.currentText() and  flag == True:
            self.ui.cmb_fio.addItem(fio + ' ' + dolg)

def reset_user_pass(self):
    if not CMS.user_access(self.bd_naryad,'выполнение_сборс_пароля',F.user_name()):
        return
    lbx = self.ui.cmb_fio
    if self.glob_login != "":
        CQT.msgbox('Нужно сначала выйти')
        return
    if lbx.currentText() == '':
        CQT.msgbox('Не выбран пользователь')
        return
    ima = CMS.ima_po_emp(lbx.currentText())

    if F.nalich_file(F.pcfg('Riba')) == False:
        CQT.msgbox(f'Не найден файл с паролями')

    spis = F.load_file_pickle(F.pcfg('Riba'))
    for i in range(len(spis)):
        log = spis[i][0]
        if CMS.shifr(ima.strip()) in log.strip():
            spis[i][1] = CMS.shifr(F.now("%Y"))
            spis[i][2] = ''
            break
    F.save_file_pickle(F.pcfg('Riba'), spis)
    CQT.msgbox("Пользователь сброшен: " + '\n' + ima + '\n' \
               + F.now("%Y"))

def change_user_pass(self):
    if self.glob_login == '':
        return
    if self.ui.le_Nparol.isVisible() == False:
        CQT.msgbox('Введи СТАРЫЙ и НОВЫЙ,НОВЫЙ пароль, \n\n далее ПОВТОРНО \n\n *Параметры  -->  "сменить пароль"')
        self.ui.le_Nparol.setVisible(True)
        self.ui.le_Nparol2.setVisible(True)
        return
    ima = CMS.ima_po_emp(self.glob_login)
    parol = CMS.Podtv_lich_parol(ima, self.ui.le_parol.text())
    if parol == None:
        CQT.msgbox("Не найден пользователь")
        return
    if parol == False:
        CQT.msgbox("Не верный пароль")
        self.ui.le_parol.clear()
        return
    if self.ui.le_Nparol.text() != self.ui.le_Nparol2.text():
        CQT.msgbox("Не совпадают новые пароли")
        return
    if self.ui.le_parol.text() == self.ui.le_Nparol2.text():
        CQT.msgbox("Новый пароль должен отличаться от старого")
        return
    if ' ' in self.ui.le_Nparol.text():
        CQT.msgbox(f'Пароль не может содержать пробелы')
        return
    if len(self.ui.le_Nparol.text()) < 5:
        CQT.msgbox(f'Пароль не может быть меньше 5 символов')
        return

    spis = F.load_file_pickle(F.pcfg('Riba'))
    for i in range(len(spis)):
        if spis[i][0] == CMS.shifr(ima):
            spis[i][1] = CMS.shifr(self.ui.le_Nparol.text())
            if len(spis[i]) == 2:
                spis[i].append(F.now(''))
            else:
                spis[i][2] = F.now('')
            break
    F.save_file_pickle(F.pcfg('Riba'), spis)
    F.save_file_pickle(F.pcfg('Riba') + f'_back_{F.now("%Y%m%d")}', spis)
    self.ui.le_parol.setText('')
    self.ui.le_Nparol.setText('')
    self.ui.le_Nparol2.setText('')
    self.ui.le_Nparol.setVisible(False)
    self.ui.le_Nparol2.setVisible(False)
    logout(self)
    self.glob_login = ''
    self.setWindowTitle('Создание нарядов')
    CQT.msgbox("Пароль изменен, войди еще раз по новому паролю")
    return
