from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWinExtras import QtWin
import os
import user_mange as userm
import project_cust_38.Cust_Qt as CQT
CQT.conver_ui_v_py()
from mydesign import Ui_MainWindow  # импорт нашего сгенерированного файла
import config
import sys
import project_cust_38.Cust_Functions as F
import project_cust_38.Cust_SQLite as CSQ
import project_cust_38.Cust_mes as CMS
import project_cust_38.Cust_QtGui as CGUI
from datetime import timedelta
from datetime import datetime as DT
from project_cust_38.otcheti import virabotka_sotr
cfg = config.Config('Config\CFG.cfg')  # файл конфига, находится п папке конфиг

F.test_path()

class mywindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(mywindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.versia =  '1.4.4.1'
        # ===========================================connects
        # ==================BTN
        self.ui.btn_login.clicked.connect(lambda _, x=self: userm.log_in(x))
        self.ui.btn_logout.clicked.connect(lambda _, x=self: userm.logout(x))
        self.ui.btn_nachat.clicked.connect(self.nachat_nar)
        self.ui.btn_pauza.clicked.connect(self.pauza_nar)
        self.ui.btn_zaconch.clicked.connect(self.zaversh_nar)
        self.ui.btn_otkr_kd.clicked.connect(self.otkrit_docs)
        self.ui.btn_obnov_sp_nar.clicked.connect(self.zapoln_tabl_naryadov)
        #===================COMBOBOX
        self.ui.cmb_dolgn.activated[int].connect(lambda _, x = self: userm.load_po_dolg(x))
        self.ui.cmb_zamechain.activated[int].connect(self.vibor_zamech)
        #==== GLOBALS
        self.glob_login = ''
        self.glob_fio = ''
        self.user_score = None
        self.glob_summ_treb_chas_tabel = 0

        # =======tbls
        self.ui.tbl_naryadi.cellDoubleClicked[int,int].connect(self.load_naruad)
        self.ui.tbl_naryadi.clicked.connect(self.tbl_naryadi_click)
        self.ui.tbl_chert.cellDoubleClicked[int, int].connect(self.otkrit_kd)
        self.ui.tbl_td.cellDoubleClicked[int, int].connect(self.otkrit_td)
        self.ui.tbl_naryadi_view_kompl.clicked.connect(self.tbl_komplektovka_view_click)
        # =======tabs
        self.ui.tabWidget_2.currentChanged[int].connect(self.tab2_clcik)
        self.ui.tabWidget.currentChanged[int].connect(self.tab_clcik)
        self.ui.tabWidget_3.currentChanged[int].connect(self.tab_clcik3)
        self.ui.tabWidget_docs.currentChanged[int].connect(self.tbl_prosmotr_docs)
        # ========le
        self.ui.le_basa.textChanged.connect(self.calc_user_score)
        self.ui.le_premia.textChanged.connect(self.calc_user_score)
        self.ui.le_brak.textChanged.connect(self.calc_user_score)

        #======ACTIONS
        self.ui.action_noviy_user.triggered.connect(lambda _, x = self: userm.reg_new_user(x))
        self.ui.action_change_pass.triggered.connect(lambda _, x = self: userm.change_user_pass(x))
        self.ui.action_reset_parol.triggered.connect(lambda _, x=self: userm.reset_user_pass(x))
        self.ui.peresilniy.triggered.connect(self.create_peresilniy)
        self.ui.ved_komplekt.triggered.connect(self.create_ved_komplekt)
        self.ui.zayav_pererabotchik.triggered.connect(self.create_zayav_pererab)
        # ============DB
        self.db_naryd = F.bdcfg('Naryad')
        self.bd_naryad = self.db_naryd
        self.bd_users = F.bdcfg('BD_users')
        self.db_resxml = F.bdcfg('db_resxml')
        self.db_dse = F.bdcfg('BD_dse')
        #self.db_mk = F.bdcfg('bd_mk')
        #self.db_dse = F.bdcfg('BD_dse')
        self.db_act = F.scfg('BDact') + F.sep() + 'BDact.db'
        # =======loads
        conn,cur = CSQ.connect_bd(self.db_naryd,100)
        self.check_lock_db(CMS.dict_etapi(self, self.db_naryd,""),"","")
        CSQ.close_bd(conn,cur)
        conn,cur = CSQ.connect_bd(self.bd_users)
        self.check_lock_db(userm.load_users(self,conn=conn, cur = cur), conn,cur)
        self.check_lock_db(CMS.dict_professions(self, self.bd_users, conn=conn), conn,cur)
        CSQ.close_bd(conn,cur)
        self.DICT_EMPL_FULL = CMS.dict_emploee_full(self.bd_users)
        userm.load_po_dolg(self)
        self.setWindowTitle('Создание нарядов')

        self.app_icons()
        self.ui.le_Nparol.setVisible(False)
        self.ui.le_Nparol2.setVisible(False)

        self.ui.tbl_chert.setSelectionBehavior(1)
        CQT.ust_cvet_videl_tab(self.ui.tbl_chert, r=80, g=200, b=110)
        self.ui.tbl_td.setSelectionBehavior(1)
        CQT.ust_cvet_videl_tab(self.ui.tbl_td, r=80, g=200, b=110)
        self.ui.lbl_instruction_docs.setText(f'Для ШГ и АО - srv-docs.powerz.ru:21361'
                                                f'  Для КТ и ЛК - srv-docs.powerz.ru'
                                                f'  Для КЛ и ТППР - srv-docs-pkb.powerz.ru')
        CQT.load_css(self)
        # ====ВРЕМЕННО
        self.ui.cmb_dolgn.setCurrentIndex(4)
        #self.proverka_zakritiya_naryadov_po_jurnaly()
        #self.ui.cmb_fio.setCurrentIndex(3)
        #self.ui.le_parol.setText('2022')
        #userm.log_in(self)
        #self.ui.btn_nekomplect.setEnabled(False)

    @CQT.onerror
    def check_lock_db(self,func, conn = '', cur = ''):
        rez = func
        if rez == False:
            CSQ.close_bd(conn,cur)
            CQT.msgbox(f'Нет доступа к БД попробуй позже')
            quit()

    def keyReleaseEvent(self, e):
        if e.key() == 16777237 and e.modifiers() == (QtCore.Qt.ControlModifier):
            if CQT.focus_is_QTableWidget():
                for i in range(QtWidgets.QApplication.focusWidget().rowCount()):
                    if QtWidgets.QApplication.focusWidget().rowHeight(i) > 0.5:
                        QtWidgets.QApplication.focusWidget().setRowHeight(i,QtWidgets.QApplication.focusWidget().rowHeight(i) - 1)
        if e.key() == 16777235 and e.modifiers() == (QtCore.Qt.ControlModifier):
            if CQT.focus_is_QTableWidget():
                for i in range(QtWidgets.QApplication.focusWidget().rowCount()):
                    QtWidgets.QApplication.focusWidget().setRowHeight(i,QtWidgets.QApplication.focusWidget().rowHeight(i) + 1)

        if e.key() == 67 and e.modifiers() == (QtCore.Qt.ControlModifier | QtCore.Qt.ShiftModifier):
            if CQT.focus_is_QTableWidget():
                CQT.copy_bufer_table(QtWidgets.QApplication.focusWidget())
        if self.ui.tbl_stat_filtr.hasFocus():
            if e.key() == 16777220:
                CMS.primenit_filtr(self,self.ui.tbl_stat_filtr,self.ui.tbl_stat)
        if self.ui.le_parol.hasFocus():
            if e.key() == 16777220:
                self.ui.btn_login.setFocus()
                userm.log_in(self)

    def app_icons(self):
        self.ui.btn_login.setIcon(QtGui.QIcon(QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.SP_DialogYesButton)))
        self.ui.btn_login.setIconSize(QtCore.QSize(32, 32))
        self.ui.btn_obnov_sp_nar.setIcon(
            QtGui.QIcon(QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.SP_BrowserReload)))
        self.ui.btn_obnov_sp_nar.setIconSize(QtCore.QSize(32, 32))

        self.ui.btn_nachat.setIcon(
            QtGui.QIcon(QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.SP_MediaPlay)))
        self.ui.btn_nachat.setIconSize(QtCore.QSize(64, 64))

        self.ui.btn_pauza.setIcon(
            QtGui.QIcon(QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.SP_MediaPause)))
        self.ui.btn_pauza.setIconSize(QtCore.QSize(64, 64))

        self.ui.btn_zaconch.setIcon(
            QtGui.QIcon(QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.SP_MediaStop)))
        self.ui.btn_zaconch.setIconSize(QtCore.QSize(64, 64))

        self.ui.btn_logout.setIcon(
            QtGui.QIcon(QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.SP_DialogNoButton)))
        self.ui.btn_logout.setIconSize(QtCore.QSize(32, 32))
        self.ui.tabWidget_2.setTabIcon(0, QtGui.QIcon(
            QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.SP_FileDialogDetailedView)))
        self.ui.tabWidget_2.setTabIcon(1, QtGui.QIcon(
            QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.SP_FileDialogListView)))
        self.ui.tabWidget_2.setTabIcon(2, QtGui.QIcon(
            QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.SP_MessageBoxQuestion)))
        self.ui.tabWidget.setTabIcon(0, QtGui.QIcon(
            QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.SP_DialogOkButton)))
        self.ui.tabWidget.setTabIcon(1, QtGui.QIcon(
            QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.SP_FileDialogInfoView)))
        self.ui.tabWidget.setTabIcon(2, QtGui.QIcon(
            QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.SP_FileDialogStart)))


    @CQT.onerror
    def tab_clcik3(self,ind,*args):
        if self.glob_login == "":
            return
        name = self.ui.tabWidget_3.tabText(ind)
        CQT.statusbar_text(self)
        if name == 'Предыдущий месяц':
            dat = F.datetostr(F.add_months(DT.today(),-1))
            self.load_statistic(dat,self.ui.tbl_stat_last,self.ui.tbl_stat_filtr_last)
            tbl = self.ui.tbl_stat_last
            CMS.primenit_summ(self, tbl)
            CQT.cvet_cell_wtabl(tbl, 'Внеплан', '1', r=222, g=100, b=100)
            CQT.cvet_cell_wtabl(tbl, 'Внеплан', '2', r=100, g=222, b=100)
            CQT.cvet_cell_wtabl(tbl, 'Подтвержд_вып', '0', r=222, g=100, b=100)
            CQT.cvet_cell_wtabl(tbl, 'Подтвержд_вып', '1', r=100, g=222, b=100)

    @CQT.onerror
    def tab_clcik(self,ind,*args):
        name = self.ui.tabWidget.tabText(ind)
        CQT.statusbar_text(self)
        if name == 'История наряда':
            self.history_nar_load()
        if name == 'Документация':
            self.tbl_prosmotr_docs()


    @CQT.onerror
    def tab2_clcik(self,ind,*args):
        if CMS.kontrol_ver(self.versia, "Выполнение2") == False:
            sys.exit()
        CQT.statusbar_text(self)
        name = self.ui.tabWidget_2.tabText(ind)
        self.ui.le_basa.clear()
        self.ui.le_premia.clear()
        self.ui.le_brak.clear()
        self.ui.lbl_itog_calc.clear()
        CQT.clear_tbl(self.ui.tbl_naryadi_view_kompl)
        self.ui.lbl_kompl_info.clear()
        if name == 'Доступные наряды':
            CQT.ust_cvet_obj(self.ui.lbl_ostalos)
            self.ui.lbl_ostalos.setText('')
        if name == 'Управление нарядом':
            tbl = self.ui.tbl_naryadi
            if tbl.currentRow() == -1:
                CQT.msgbox('Не выбран наряд')
                tab = self.ui.tabWidget_2
                tab.setCurrentIndex(CQT.nom_tab_po_imen(tab, 'Доступные наряды'))
                return
            self.load_naruad(tbl.currentRow(),1)
        if name == 'Статистика':
            if self.glob_login == "":
                pass
            else:
                if self.ui.tabWidget_3.tabText(self.ui.tabWidget_3.currentIndex()) == 'Предыдущий месяц':
                    dat = F.datetostr(F.add_months(DT.today(), -1))
                    self.load_statistic(dat, self.ui.tbl_stat_last, self.ui.tbl_stat_filtr_last)
                    tbl = self.ui.tbl_stat_last
                else:
                    dat = F.datetostr(DT.today())
                    self.load_statistic(dat,self.ui.tbl_stat,self.ui.tbl_stat_filtr)
                    tbl = self.ui.tbl_stat
                CMS.primenit_summ(self, tbl)
                CQT.cvet_cell_wtabl(tbl, 'Внеплан', '1', r=222, g=100, b=100)
                CQT.cvet_cell_wtabl(tbl, 'Внеплан', '2', r=100, g=222, b=100)
                CQT.cvet_cell_wtabl(tbl, 'Подтвержд_вып', '0', r=222, g=100, b=100)
                CQT.cvet_cell_wtabl(tbl, 'Подтвержд_вып', '1', r=100, g=222, b=100)

    def load_statistic(self,dat:str,tbl,filtr):
        konec = F.nach_kon_date(date=dat, vid='m')[1]
        nach = F.nach_kon_date(date=dat, vid='m')[0]
        rez_spis = virabotka_sotr(self, nach, konec, self.glob_login.replace(',', ' '))
        if rez_spis == None:
            return
        #nk_effect = F.nom_kol_po_im_v_shap(rez_spis, 'Дата')
        #nk_potabel = F.nom_kol_po_im_v_shap(rez_spis, 'Примеч_журнал')
        #nk_prem = F.nom_kol_po_im_v_shap(rez_spis, 'Задание')
        #effect = rez_spis[-2][nk_effect].split()[1]
        #potabel = F.valm(rez_spis[-2][nk_potabel].split()[2])
        #prem = rez_spis[-2][nk_prem]
        CQT.zapoln_wtabl(self, rez_spis, tbl, separ='', isp_shapka=True, max_vis_row=500)
        CMS.zapolnit_filtr(self, filtr, tbl)
        #self.load_info_imge(effect, potabel, prem)


    @CQT.onerror
    def load_info_imge(self,effect,potabel,prem):
        imgg = self.ui.lbl_fon
        imgg.clear()
        putf = os.path.join("icons", "svitok.jpg")
        if F.nalich_file(putf) == False:
            CQT.msgbox('Не найден файл фона')
            return
        pixmap, k_w, k_h = CGUI.sozdat_obj_pod_risovane(putf, imgg)
        pixmap, self.user_score = self.risovat_pixmap(pixmap, k_w, k_h,effect,potabel,prem)
        if pixmap == None:
            return
        CGUI.zagruzit_img_na_lbl(imgg, pixmap)

    @CQT.onerror
    def summ_chas_po_tabel_mes(self):
        fio = CMS.ima_po_emp(self.glob_login)
        spis_prem = F.otkr_f(F.scfg('employee') + F.sep() + 'Virabotka_sbdn.txt', separ='|')
        if spis_prem == ['']:
            return
        nk_summ_chas = F.nom_kol_po_im_v_shap(spis_prem,'stavka_tab_chas')
        nk_fio = F.nom_kol_po_im_v_shap(spis_prem, 'fio')
        for i in range(len(spis_prem)):
            if spis_prem[i][nk_fio] == fio:
                self.glob_summ_treb_chas_tabel = spis_prem[i][nk_summ_chas]
                return
        return

    @CQT.onerror
    def raschet_stoimosti_naryada(self):
        tblk = self.ui.tbl_naryadi
        r = tblk.currentRow()
        nk_koef_slog = CQT.nom_kol_po_imen(tblk, 'Коэфф_сложности')
        koef_slog = F.valm(tblk.item(r, nk_koef_slog).text())
        list_time_oper = tblk.item(r, CQT.nom_kol_po_imen(tblk,'Опер_время')).text().split('|')
        list_vid_rab_name = tblk.item(r, CQT.nom_kol_po_imen(tblk, 'Виды_работ')).text().split('|')
        summ = 0
        if len(list_time_oper) != len(list_vid_rab_name):
            return 0
        for i in range(len(list_vid_rab_name)):
            vid = list_vid_rab_name[i]
            time = F.valm(list_time_oper[i])
            if vid == '':
                continue
            if vid not in self.DICT_VID_RABOT:
                print(f'{vid} не в списке видов')
                continue
            stavka = self.DICT_VID_RABOT[vid]['руб_мин']
            summ += stavka*time
        return round(summ*koef_slog)


    @CQT.onerror
    def check_dostupnosti_nar(self,nom_nar:int):
        zapros = f'''SELECT Пномер FROM naryad WHERE Пномер == {nom_nar} AND (ФИО=="{CMS.ima_po_emp(self.glob_login)}" AND Фвремя == "" 
                                OR ФИО2=="{CMS.ima_po_emp(self.glob_login)}" AND Фвремя2 == "")'''
        rez = CSQ.zapros(self.db_naryd, zapros)
        if rez == False:
            return False
        if rez == None:
            return False
        if len(rez)>1:
            return True
        return False


    def vigruzka_trudozatrat_3(self,conn='', cur = ''):
        spis_rez = []
        #if F.strtodate(F.now()) - timedelta(days=70) > F.strtodate('2022-11-01 00:00:01'):
        data_nach = F.datetostr(F.strtodate(F.now()) - timedelta(days=40))
        #else:
        #    data_nach = '2022-11-01 00:00:01'
        zapros = f'SELECT jurnal.Дата, ' \
                 f'jurnal.Штамп, ' \
                 f'jurnal.Номер_наряда, ' \
                 f'jurnal.ФИО, ' \
                 f'mk.Номер_проекта || "$" || ' \
                 f'mk.Номер_заказа AS "НП$ПУ", ' \
                 f'naryad.Операции, ' \
                 f'naryad.Номер_мк, ' \
                 f'naryad.Виды_работ, ' \
                 f'jurnal.Статус, ' \
                 f'naryad.Твремя, ' \
                 f'jurnal.Подытог, ' \
                 f'jurnal.Примечание, ' \
                 f'naryad.Опер_время,' \
                 f'naryad.ДСЕ,' \
                 f'naryad.Виды_работ' \
                 f' FROM jurnal INNER JOIN naryad' \
                 f' ON jurnal.Номер_наряда = naryad.Пномер' \
                 f' INNER JOIN mk' \
                 f' ON naryad.Номер_мк = mk.Пномер' \
                 f' WHERE jurnal.Статус == "Начат" AND naryad.Операции NOT LIKE "%Резка(ЧПУ)%" AND jurnal.Подытог > 0 and date(jurnal.Дата) > date("{data_nach}")'

        rez = CSQ.zapros(self.db_naryd, zapros,rez_dict=True,conn=conn, cur = cur)
        if rez == False or rez == None:
            return
        set_etapov = set()
        for i in range(1, len(rez)):
            dolgn = self.DICT_EMPLOEE[rez[i]['ФИО']]
            etap = self.DICT_PROFESSIONS_PSEUDONAME[dolgn]['этап']
            fiod = self.fiod(rez[i]['ФИО'])
            spis_dse =  rez[i]['ДСЕ'].split('|')[0]
            spis_rez.append([rez[i]['Дата'], rez[i]['Штамп'], rez[i]['Номер_наряда'], fiod, rez[i]['НП$ПУ'],
                             etap, spis_dse, rez[i]['Статус'],
                             rez[i]['Подытог'], "Основной ФОТ", F.ochist_strok_pod_ima_fila(rez[i]['Примечание'])])
            set_etapov.add(etap)

        for etap in set_etapov:
            tmp = []
            for item in spis_rez:
                if etap == item[5]:
                    tmp.append(item)
            F.save_file(F.scfg('employee') + F.sep() + f'Trudozatrati_3_{etap}.txt', tmp,utf=False)
        #F.zap_f(F.scfg('employee') + F.sep() + 'Trudozatrati.txt', spis_rez,separ='|',utf8=False)


    @CQT.onerror
    def fiod(self,fio_):
        dolgn = f'{fio_} должность'
        for item in self.SPIS_EMPLOEE:
            if fio_ == item[0]:
                return ' '.join(item)
        return dolgn

    @CQT.onerror
    def vibor_zamech(self,nom,*args):
        zam = self.ui.cmb_zamechain.itemText(nom)
        self.ui.te_zamechain.setPlainText(zam)

    @CQT.onerror
    def create_zayav_pererab(self,*args):
        if self.glob_login == "":
            CQT.msgbox('Необходимо войти')
            return
        if self.ui.tabWidget_2.currentIndex() != CQT.nom_tab_po_imen(self.ui.tabWidget_2, 'Доступные наряды'):
            self.ui.tabWidget_2.setCurrentIndex(CQT.nom_tab_po_imen(self.ui.tabWidget_2, 'Доступные наряды'))
        tbl = self.ui.tbl_naryadi
        tblv = self.ui.tbl_naryadi_view_kompl
        CMS.load_zayav_pererab(self,tbl,tblv)

    @CQT.onerror
    def create_ved_komplekt(self,*args):
        if self.glob_login == "":
            CQT.msgbox('Необходимо войти')
            return
        if self.ui.tabWidget_2.currentIndex() != CQT.nom_tab_po_imen(self.ui.tabWidget_2, 'Доступные наряды'):
            self.ui.tabWidget_2.setCurrentIndex(CQT.nom_tab_po_imen(self.ui.tabWidget_2, 'Доступные наряды'))
        tbl = self.ui.tbl_naryadi
        tblv = self.ui.tbl_naryadi_view_kompl
        CMS.load_ved_komplekt(self,tbl,tblv)

    @CQT.onerror
    def create_peresilniy(self,*args):
        if self.glob_login == "":
            CQT.msgbox('Необходимо войти')
            return
        if self.ui.tabWidget_2.currentIndex() != CQT.nom_tab_po_imen(self.ui.tabWidget_2, 'Доступные наряды'):
            self.ui.tabWidget_2.setCurrentIndex(CQT.nom_tab_po_imen(self.ui.tabWidget_2, 'Доступные наряды'))
        tbl = self.ui.tbl_naryadi
        tblv = self.ui.tbl_naryadi_view_kompl
        CMS.load_peresilniy(self,tbl,tblv)


    @CQT.onerror
    def calc_user_score(self,*args):
        basa = self.ui.le_basa.text()


        premia = self.ui.le_premia.text()
        brak = self.ui.le_brak.text()
        itog = self.ui.lbl_itog_calc

        itog.setText('-')
        if self.glob_login == "":
            return

        if F.is_numeric(basa) == False:
            return

        if F.is_numeric(premia) == False:
            return
        if F.is_numeric(brak) == False:
            return

        rez = round(F.valm(basa)*(F.valm(premia)-abs(F.valm(brak)))/100)
        itog.setText(str(rez))

    @CQT.onerror
    def risovat_pixmap(self,pixmap,k_w,k_h,effect,potabel,prem):
        fio = CMS.ima_po_emp(self.glob_login)
        prof = CMS.dol_po_emp(self.glob_login)
        spis_prem = F.otkr_f(F.scfg('employee') + F.sep() + 'Virabotka_sbdn.txt', separ='|')
        spis_po_prof = []
        my_paramets =''
        for i in range(1,len(spis_prem)):
            if prof == spis_prem[i][1]:
                spis_po_prof.append(spis_prem[i])
                if spis_prem[i][0] in fio:
                    my_paramets = spis_prem[i]
        for i in range(len(spis_po_prof)):
            spis_po_prof[i].append(round(int(spis_po_prof[i][2])-int(spis_po_prof[i][3])*2))
        spis_po_prof.sort(key=lambda x:int(x[-1]), reverse = True)

        qpp = QtGui.QPainter(pixmap)
        nach = [round(205 * k_w), round(113 * k_h)]
        font1 = round(30 * k_h)
        font2 = round(36 * k_h)
        shag1 = font1 *1.6


        CGUI.ris_text(qpp,nach[0],nach[1],f'Топ 5 по профессии {prof},  баллов.:',10,10,10,font1,ima_font='Century')
        nach[1] += shag1*2
        top = 6
        if len(spis_po_prof) < top:
            top = len(spis_po_prof)
        try:
            for i in range(top):
                CGUI.ris_text(qpp, nach[0] , nach[1] + i * shag1, f'{spis_po_prof[i][0]} \n {spis_po_prof[i][-1]}' , 10, 10, 10, font2, ima_font='Bookman Old Style')
        except:
            return None, None
        if my_paramets == "":
            return None, None
        nach2 = [round(205 * k_w), round(559 * k_h)]
        nach3 = [round(1120 * k_w), round(113 * k_h)]
        CGUI.ris_text(qpp, nach2[0], nach2[1], f'Статистика, {fio}:', 10, 10, 10, font2,
                      ima_font='Bookman Old Style')
        nach2[1] += shag1 * 2
        CGUI.ris_text(qpp, nach2[0], nach2[1], f'{prem}', 10, 10, 10, font2,
                      ima_font='Bookman Old Style')
        nach2[1] += shag1 * 2
        qpp.drawText(int(nach3[0]), int(nach3[1]), int(900* k_w), int(999 * k_w), 0x1000,
                     f'Выполненые наряды, №-час.:  {my_paramets[4].replace(":","-").replace(";",";   ")}')
        nach2[1] += shag1 * 2
        CGUI.ris_text(qpp, nach2[0], nach2[1], f'Эффективность {effect}', 10, 10, 10, font2,
                      ima_font='Bookman Old Style')
        nach2[1] += shag1 * 2
        CGUI.ris_text(qpp, nach2[0], nach2[1], f'Акты о браке,№-вычет: {my_paramets[6]}', 10, 10, 10, font2,
                      ima_font='Bookman Old Style')
        nach2[1] += shag1 * 2
        CGUI.ris_text(qpp, nach2[0], nach2[1], f'Итого за брак:, {my_paramets[3]}', 10, 10, 10, font2,
                      ima_font='Bookman Old Style')
        nach2[1] += shag1 * 2
        CGUI.ris_text(qpp, nach2[0], nach2[1], f'Минут по табелю к работе: {potabel} ({round(potabel/480,1)} смен)', 10, 10, 10, font2,
                      ima_font='Bookman Old Style')
        nach2[1] += shag1 * 2
        CGUI.ris_text(qpp, nach2[0], nach2[1], f'Баллов по профессии: {my_paramets[8]}', 10, 10, 10, font2,
                      ima_font='Bookman Old Style')
        qpp.end()
        return pixmap, my_paramets

    @CQT.onerror
    def history_nar_load(self):
        if self.ui.lbl_nom_nar.text() == '':
            return
        nom_nar = int(self.ui.lbl_nom_nar.text())
        zapros = f'''SELECT  Дата, ФИО, Статус, Подытог, Примечание FROM jurnal WHERE Номер_наряда == {nom_nar}'''
        rez = CSQ.zapros(self.db_naryd, zapros)
        CQT.zapoln_wtabl(self, rez, self.ui.tbl_history, isp_shapka=True, separ='',min_shir_col=200)


    @CQT.onerror
    def tbl_prosmotr_docs(self,*args):
        if self.ui.tabWidget_docs.currentIndex() == CQT.nom_tab_po_imen(self.ui.tabWidget_docs,'КД'):
            self.prosmotr_kd_load()
        if self.ui.tabWidget_docs.currentIndex() == CQT.nom_tab_po_imen(self.ui.tabWidget_docs,'ТД'):
            self.prosmotr_td_load()

    @CQT.onerror
    def prosmotr_td_load(self):
        tblp = self.ui.tbl_td
        if self.ui.lbl_nom_nar.text() == '':
            return
        nom_nar = int(self.ui.lbl_nom_nar.text())
        zapros = f'''SELECT ДСЕ,Операции,Номер_мк FROM naryad WHERE Пномер == {nom_nar}'''
        rez = CSQ.zapros(self.db_naryd, zapros)
        spis_kd = rez[-1][0].split('|')
        spis_oper = rez[-1][1].split('|')
        nom_mk = rez[-1][2]
        set_docs = set()

        res = CMS.load_res(nom_mk)

        for i in range(len(spis_kd)):
            naim , nn = spis_kd[i].split('$')
            nom_oper = spis_oper[i].split('$')[0]
            for dse in res:
                if dse['Номенклатурный_номер'] == nn and dse['Наименование'] == naim:
                    for oper in dse['Операции']:
                        if nom_oper == oper['Опер_номер']:
                            for doc in oper['Опер_документы']:
                                if doc != '':
                                    set_docs.add(doc)
                            break
                    break
        spis_docs =[[x] for x in sorted(list(set_docs))]
        spis_docs.insert(0,['Документы'])
        CQT.zapoln_wtabl(self, spis_docs, tblp, isp_shapka=True, separ='', ogr_maxshir_kol=300)

    @CQT.onerror
    def prosmotr_kd_load(self):
        tblp = self.ui.tbl_chert
        if self.ui.lbl_nom_nar.text() == '':
            return
        nom_nar = int(self.ui.lbl_nom_nar.text())


        zapros = f'''SELECT ДСЕ FROM naryad WHERE Пномер == {nom_nar}'''
        rez = CSQ.zapros(self.db_naryd,zapros)

        list_dse = CSQ.zapros(self.db_dse,"""SELECT Путь_docs,Номенклатурный_номер FROM dse""", rez_dict=True)

        dict_dse = F.raskrit_dict(list_dse, 'Номенклатурный_номер')

        spis_kd = rez[-1][0].split('|')
        rez_shap = ['НН',"Наименование",'Путь']
        rez_set = set()

        for dse in spis_kd:
            tmp = dse.split('$')
            put_docs = dict_dse[tmp[1]]
            rez_set.add((tmp[0],tmp[1],put_docs))

        rez_spis = list(rez_set)
        rez_spis.insert(0,rez_shap)
        CQT.zapoln_wtabl(self,rez_spis,tblp,isp_shapka=True,separ='',ogr_maxshir_kol=300)


    @CQT.onerror
    def otkrit_docs(self,*args):
        if self.ui.tabWidget_docs.currentIndex() == CQT.nom_tab_po_imen(self.ui.tabWidget_docs,'КД'):
            self.otkrit_kd()
        if self.ui.tabWidget_docs.currentIndex() == CQT.nom_tab_po_imen(self.ui.tabWidget_docs,'ТД'):
            self.otkrit_td()

    @CQT.onerror
    def otkrit_td(self,*args):
        tbl = self.ui.tbl_td
        if tbl.currentRow() == -1:
            return
        name = tbl.item(tbl.currentRow(),0).text()
        spis_files = F.spis_files(F.scfg('td'))
        for file in spis_files[0][2]:
            if name == F.ubrat_rasshir(file):
                F.zapyst_file(spis_files[0][0] + F.sep() + file)
                return
        CQT.msgbox(f'Файл {name} не найден')


    @CQT.onerror
    def otkrit_kd(self,*args):
        tbl = self.ui.tbl_chert
        if tbl.currentRow() == -1:
            return
        nk_ssil = CQT.nom_kol_po_imen(tbl,'Путь')
        ssil = tbl.item(tbl.currentRow(),nk_ssil).text()
        os.startfile(f"{ssil}")

    @CQT.onerror
    def clear_naryad_bar(self,conn ='',cur = ''):
        self.lbl_tek_narayd(CMS.ima_po_emp(self.glob_login))
        tab = self.ui.tabWidget_2
        #tab.setCurrentIndex(CQT.nom_tab_po_imen(tab, 'Доступные наряды'))
        self.ui.lbl_nom_nar.setText("")
        self.ui.lbl_sozdan.setText("")
        self.ui.lbl_proekt.setText("")
        self.ui.lbl_norma.setText("")
        self.ui.lbl_nom_mk.setText("")
        self.ui.lbl_isp1.setText("")
        self.ui.lbl_isp2.setText("")
        self.ui.textBrowser_zadanie.setText("")
        self.ui.te_zamechain.clear()

    @CQT.onerror
    def time_ostalos_po_nar(self):
        tblk = self.ui.tbl_naryadi
        tblv = self.ui.tbl_naryadi_view_kompl
        if tblk.currentRow() == -1:
            CQT.msgbox('Не выбран наряд')
            return
        r = tblk.currentRow()
        nk_nar = CQT.nom_kol_po_imen(tblk, 'Пномер')
        nk_tvrem = CQT.nom_kol_po_imen(tblk, 'Твремя')
        nk_mk = CQT.nom_kol_po_imen(tblk, 'Номер_мк')
        if tblk.item(r,nk_nar).text() == '-':
            return
        nom_nar = int(tblk.item(r,nk_nar).text())
        tvrema = F.valm(tblk.item(r,nk_tvrem).text())
        rub = self.raschet_stoimosti_naryada()
        if rub > 0:
            rub_format = str(rub/1000).replace('.',' ')
            CQT.statusbar_text(self,f'Наряд №{nom_nar}, предварительно расценен на {rub_format} рублей',18,text_color='red')
        else:
            CQT.statusbar_text(self)

        conn, cur = CSQ.connect_bd(self.db_naryd,2)
        if int(tblk.item(r,nk_mk).text()) != 0:
            CMS.specificaciya_naruad(self, tblk, tblv,conn='',cur='')
        zapros = f'''SELECT sum(Подытог) AS "Total Salary" FROM jurnal WHERE Номер_наряда == {nom_nar} AND ФИО == "{CMS.ima_po_emp(self.glob_login)}"'''
        rez = CSQ.zapros(self.db_naryd,zapros,conn=conn,cur=cur)
        zapros = f'''SELECT Штамп, Статус FROM jurnal WHERE Номер_наряда == {nom_nar} AND ФИО == "{CMS.ima_po_emp(self.glob_login)}" ORDER BY Пномер DESC LIMIT 1'''
        rez_last = CSQ.zapros(self.db_naryd, zapros,conn=conn,cur = cur)
        CSQ.close_bd(conn,cur)

        if rez == False or rez_last == False:
            CQT.msgbox(f'Не удалось получить подытог')
            return
        tfakt = 0
        if len(rez) > 1:
            if rez[-1][0] != None:
                tfakt = rez[-1][0]
        t_zadel = 0
        if len(rez_last) > 1:
            if rez_last[-1][1] == "Начат":
                t_zadel = (F.time_metka() - rez_last[-1][0])//60
        raznica = tvrema-tfakt-t_zadel
        if raznica < 0:
            CQT.ust_cvet_obj(self.ui.lbl_ostalos,111,221,111)
            self.ui.lbl_ostalos.setText(f'По №{str(nom_nar)} дефицит {abs(raznica)} мин. НЕ ЗАКРЫВАЙ наряд, не доделав до конца работу. иначе за простой придется отчитываться.')
        else:
            CQT.ust_cvet_obj(self.ui.lbl_ostalos)
            self.ui.lbl_ostalos.setText(f'По №{str(nom_nar)} осталось {raznica} мин.')
        font = QtGui.QFont()
        font.setPointSize(14)
        self.ui.lbl_ostalos.setFont(font)


    @CQT.onerror
    def tbl_naryadi_click(self,*args):
        CQT.statusbar_text(self)
        self.time_ostalos_po_nar()
        #F.sleep(3)


    @CQT.onerror
    def tbl_komplektovka_view_click(self,*args):
        tblv = self.ui.tbl_naryadi_view_kompl
        r = tblv.currentRow()
        nk_dse = CQT.nom_kol_po_imen(tblv, 'Операции')
        self.ui.lbl_kompl_info.setText(tblv.item(r,nk_dse).text())

    @CQT.onerror
    def open_dir_chpy(self, line:str):
        if line == '':
            return
        try:
            path = '_'.join(line.split('_')[2:])
            if F.nalich_file(path):
                F.otkr_papky(path)
        except:
            CQT.msgbox(f'Ошибка обработки строки')

    def load_prostoy_nar(self):
        tbl = self.ui.tbl_naryadi
        tab = self.ui.tabWidget_2
        r = tbl.currentRow()
        nk_dat = CQT.nom_kol_po_imen(tbl, 'Дата')
        nk_np = CQT.nom_kol_po_imen(tbl, 'Номер_проекта')
        nk_nz = CQT.nom_kol_po_imen(tbl, 'Номер_заказа')
        nk_vrem = CQT.nom_kol_po_imen(tbl, 'Твремя')
        nk_nom_mk = CQT.nom_kol_po_imen(tbl, 'Номер_мк')
        nk_fio = CQT.nom_kol_po_imen(tbl, 'ФИО')
        nk_fio2 = CQT.nom_kol_po_imen(tbl, 'ФИО2')
        nk_zadanie = CQT.nom_kol_po_imen(tbl, 'Задание')

        sozdan = tbl.item(r, nk_dat).text()
        proj = tbl.item(r, nk_np).text() + ' ' + tbl.item(r, nk_nz).text()
        vrem = tbl.item(r, nk_vrem).text()
        mk = tbl.item(r, nk_nom_mk).text()
        fio = tbl.item(r, nk_fio).text()
        fio2 = tbl.item(r, nk_fio2).text()
        zadanie = tbl.item(r, nk_zadanie).text()

        self.ui.lbl_nom_nar.setText(str('-'))
        self.ui.lbl_sozdan.setText(sozdan)
        self.ui.lbl_proekt.setText(proj)
        self.ui.lbl_norma.setText(vrem)
        self.ui.lbl_nom_mk.setText(mk)
        self.ui.lbl_isp1.setText(fio)
        self.ui.lbl_isp2.setText(fio2)
        self.ui.textBrowser_zadanie.setText(zadanie)
        tab.setCurrentIndex(CQT.nom_tab_po_imen(tab, 'Управление нарядом'))

    @CQT.onerror
    def load_naruad(self,r,c,*args):
        tab = self.ui.tabWidget_2
        tbl = self.ui.tbl_naryadi
        if tbl.currentRow() == -1:
            CQT.msgbox('Не выбран наряд')
            return
        if tbl.horizontalHeaderItem(c).text() == 'Статус_ЧПУ':
            self.open_dir_chpy(tbl.item(r,c).text())
            return
        nk_nar = CQT.nom_kol_po_imen(tbl, 'Пномер')
        if tbl.item(r,nk_nar).text() == '-':
            self.load_prostoy_nar()
            return
        nom_nar = int(tbl.item(r,nk_nar).text())
        conn, cur = CSQ.connect_bd(self.db_naryd)
        if self.check_dostupnosti_nar(nom_nar) == False:
            self.zapoln_tabl_naryadov()
            CSQ.close_bd(conn,cur)
            tab.setCurrentIndex(CQT.nom_tab_po_imen(tab, 'Доступные наряды'))
            CQT.msgbox('Наряд недоступен')
            return
        else:
            CSQ.close_bd(conn,cur)
            pass
        nk_dat = CQT.nom_kol_po_imen(tbl,'Дата')
        nk_np = CQT.nom_kol_po_imen(tbl, 'Номер_проекта')
        nk_nz = CQT.nom_kol_po_imen(tbl, 'Номер_заказа')
        nk_vrem = CQT.nom_kol_po_imen(tbl, 'Твремя')
        nk_nom_mk = CQT.nom_kol_po_imen(tbl, 'Номер_мк')
        nk_fio =  CQT.nom_kol_po_imen(tbl, 'ФИО')
        nk_fio2 = CQT.nom_kol_po_imen(tbl, 'ФИО2')
        nk_zadanie = CQT.nom_kol_po_imen(tbl, 'Задание')

        sozdan = tbl.item(r, nk_dat).text()
        proj = tbl.item(r, nk_np).text() + ' ' + tbl.item(r, nk_nz).text()
        vrem = tbl.item(r, nk_vrem).text()
        mk = tbl.item(r, nk_nom_mk).text()
        fio = tbl.item(r, nk_fio).text()
        fio2 = tbl.item(r, nk_fio2).text()
        zadanie = tbl.item(r, nk_zadanie).text()

        self.ui.lbl_nom_nar.setText(str(nom_nar))
        self.ui.lbl_sozdan.setText(sozdan)
        self.ui.lbl_proekt.setText(proj)
        self.ui.lbl_norma.setText(vrem)
        self.ui.lbl_nom_mk.setText(mk)
        self.ui.lbl_isp1.setText(fio)
        self.ui.lbl_isp2.setText(fio2)
        self.ui.textBrowser_zadanie.setText(zadanie)
        tab.setCurrentIndex(CQT.nom_tab_po_imen(tab, 'Управление нарядом'))

    @CQT.onerror
    def zapoln_tabl_naryadov(self,*args):
        if self.glob_login == "":

            CQT.msgbox('Необходимо войти')
            return
        zapros = f'''  SELECT naryad.Пномер, naryad.Дата, naryad.Номер_мк, naryad.Задание, naryad.ФИО, naryad.ФИО2, 
                        naryad.Твремя, naryad.Компл_номер_тара, naryad.Компл_адрес, naryad.Примечание,
                        mk.Номер_проекта, mk.Номер_заказа, mk.Приоритет, naryad.Коэфф_сложности, naryad.Виды_работ, naryad.Опер_время, mk.Статус_ЧПУ, zagot.Прим_резка
                                FROM naryad INNER JOIN mk ON mk.Пномер = naryad.Номер_мк 
                                INNER JOIN zagot ON zagot.Ном_МК = naryad.Номер_мк 
                        WHERE ((mk.Статус != "Закрыта" AND mk.Дата_завершения == "") OR (mk.Пномер = 0)) AND ((ФИО=="{CMS.ima_po_emp(self.glob_login)}" AND Фвремя == "") 
                        OR (ФИО2=="{CMS.ima_po_emp(self.glob_login)}" AND Фвремя2 == ""));'''
        rez = CSQ.zapros(self.db_naryd, zapros)
        if rez == False or rez == None:
            CQT.msgbox(f'БД недоступна, пробуй еще')
            return
        self.ui.label_12.setText(f'План работ для {CMS.ima_po_emp(self.glob_login)} на {F.now()}')
        rez = F.sort_po_kol(rez,'Приоритет')
        rez.insert(1,['-','-','-','ПРОСТОЙ',CMS.ima_po_emp(self.glob_login),'','1','','','ПРОСТОЙ','-','-','1','1.0','-','','',''])
        CQT.zapoln_wtabl(self, rez, self.ui.tbl_naryadi, separ='', isp_shapka=True)
        CQT.add_btn(self.ui.tbl_naryadi, 0, 1, 'СОЗДАТЬ', True, self.create_prostoi_nar, '')
        spis_prost = F.load_file(F.scfg('Riba') + F.sep() + 'Prich_prost.txt')
        CQT.add_combobox(self,self.ui.tbl_naryadi, 0, 5, spis_prost, True,'')
        self.ui.tbl_naryadi.setColumnHidden(CQT.nom_kol_po_imen(self.ui.tbl_naryadi, 'Задание'), True)
        self.ui.tbl_naryadi.setColumnHidden(CQT.nom_kol_po_imen(self.ui.tbl_naryadi, 'Дата'), False)
        self.ui.tbl_naryadi.setColumnHidden(CQT.nom_kol_po_imen(self.ui.tbl_naryadi, 'Виды_работ'), True)
        self.ui.tbl_naryadi.setColumnHidden(CQT.nom_kol_po_imen(self.ui.tbl_naryadi, 'Опер_время'), True)
        self.lbl_tek_narayd(CMS.ima_po_emp(self.glob_login))
        #F.sleep(3)

    def check_zav_nar(self,nom_nar,fio):
        query = f'''SELECT Дата FROM jurnal WHERE Номер_наряда == {nom_nar} and Статус == "Завершен" and ФИО == "{fio}"'''
        rez = CSQ.zapros(self.db_naryd,query,one=True)
        if len(rez) == 1 or query == False:
            return False
        return True

    def create_prostoi_nar(self,row,col):
        primech = self.ui.tbl_naryadi.cellWidget(self.ui.tbl_naryadi.currentRow(),5).currentText()
        if primech == '':
            CQT.migat_obj(self,2,self.ui.tbl_naryadi,'Не указана причина простоя')
            return False
        date_nar = F.now()
        stroka = [date_nar,
                  CMS.ima_po_emp(self.glob_login),
                  0,
                  3,
                  'ПРОСТОЙ',
                  CMS.ima_po_emp(self.glob_login),
                  date_nar,
                  '-',
                  '-',
                  CMS.ima_po_emp(self.glob_login),
                  '',
                  '',
                  '',
                  1,
                  '',
                  '',
                  '$',
                  1,
                  '',
                  primech,
                  1, 0, 10, '','']
        zapros = f'''INSERT INTO naryad (Дата,	Автор,Номер_мк,Внеплан,Задание,Компл_ФИО,Компл_Дата,Компл_номер_тара,
               Компл_адрес,ФИО,Фвремя,ФИО2,Фвремя2,Твремя,ДСЕ,ДСЕ_ID,Операции,Опер_время,Опер_колво,Примечание,Коэфф_сложности,
               Подтвержд_вып,Категория_внепл,Виды_работ,Номер_замечания_журнал) VALUES ({", ".join(("?" * len(stroka)))});'''
        # rez = CSQ.dob_strok_v_bd_sql(self.db_naryd, 'naryad', [stroka], conn= conn,cur = cur)
        rez = CSQ.zapros(self.db_naryd, zapros, spisok_spiskov=[stroka])
        if rez == False:
            CQT.msgbox(f'Не удачно, попробуй позже')
            return
        nom_nar = CSQ.zapros(self.db_naryd, f"""SELECT Пномер FROM naryad WHERE Дата = '{date_nar}' 
               AND Автор = '{CMS.ima_po_emp(self.glob_login)}' ORDER BY Пномер DESC LIMIT 1""")
        try:
            if len(nom_nar) != 2 or F.is_numeric(nom_nar[-1][0]) == False:
                CQT.msgbox(f'Неудачно!, попробуй еще.')
                return
        except:
            CQT.msgbox(f'Неудачно!, попробуй еще.')
            return

        self.zapoln_tabl_naryadov()

    @CQT.onerror
    def nachat_nar(self,*args):
        if not CMS.check_actual_parol(self.glob_fio):
            CQT.msgbox(f'Нужно обновить пароль через меню "Параметры"')
            return
        try:
            nom_nar = int(self.ui.lbl_nom_nar.text())
        except:
            CQT.msgbox(f'Наряд не выбран')
            return
        now = F.now()
        primech = self.ui.te_zamechain.toPlainText()
        if not self.check_abstrakt(primech):
            return
        stroka = [now,F.shtamp_from_date(now),nom_nar,CMS.ima_po_emp(self.glob_login),0,'Начат',primech, '']

        conn,cur = CSQ.connect_bd(self.db_naryd)
        tek = self.tekush_naruad(CMS.ima_po_emp(self.glob_login))
        if tek == False or tek ==  (False,False,False):
            CSQ.close_bd(conn,cur)
            CQT.msgbox(f'БД занята попробуй позже')
            return
        if tek[0] != '':
            CSQ.close_bd(conn,cur)
            CQT.msgbox('Нельзя начать несколько нарядов одновременно')
            return
        if self.check_zav_nar(nom_nar, CMS.ima_po_emp(self.glob_login)):
            CSQ.close_bd(conn, cur)
            CQT.msgbox(f'Наряд {nom_nar} уже завершен ранее')
            return
        tab = self.ui.tabWidget_2
        if self.check_dostupnosti_nar(nom_nar) == False:
            tab.setCurrentIndex(CQT.nom_tab_po_imen(tab, 'Доступные наряды'))
            #self.zapoln_tabl_naryadov(conn = conn,cur= cur)
            CSQ.close_bd(conn,cur)
            CQT.msgbox('Наряд недоступен')
            return

        rez = CSQ.zapros(self.db_naryd,"""INSERT INTO jurnal
                              (Дата, Штамп, Номер_наряда,ФИО,Подытог,Статус,Примечание,Ном_заверш)
                              VALUES (?, ?, ?, ?, ?, ?, ?, ?);""", conn=conn,cur=cur, spisok_spiskov=[stroka])

        #rez = CSQ.dob_strok_v_bd_sql(self.db_naryd,'jurnal',[stroka], conn=conn)
        if rez != True:
            CSQ.close_bd(conn, cur)
            CQT.msgbox(f'Не удачно попробуй чуть позже')
            F.sleep(2)
            return
        self.clear_naryad_bar(conn=conn,cur = cur)
        CSQ.close_bd(conn,cur)
        CQT.msgbox('Наряд успешно запущен')
        #F.sleep(2)

    @CQT.onerror
    def check_vibr_i_tek_nar(self):
        nomer_naryada, pnomer, data_nach = self.tekush_naruad(CMS.ima_po_emp(self.glob_login))
        if nomer_naryada == False:
            return False, False
        if str(nomer_naryada) != self.ui.lbl_nom_nar.text():
            CQT.msgbox('Выбран не запущенный наряд')
            return False, False
        return str(pnomer), data_nach

    @CQT.onerror
    def pauza_nar(self,*args):
        self.stop_nar("Приостановлен")

    @CQT.onerror
    def zaversh_nar(self,*args):
        self.stop_nar("Завершен")

    def check_abstrakt(self,primech):

        if self.glob_fio not in self.DICT_EMPL_FULL:
            CQT.msgbox(f'{self.glob_fio} не в БД')
            return False
        if self.DICT_EMPL_FULL[self.glob_fio]['Режим'] == 'Абстракт':
            if primech == '':
                CQT.msgbox(f'Не выбрано реальное ФИО в Примечании')
                return False
            if primech not in self.DICT_EMPL_FULL:
                CQT.msgbox(f'{primech} не в БД')
                return False
        return True

    @CQT.onerror
    def stop_nar(self, vid_stop):

        try:
            pnomer_nach, data_nach = self.check_vibr_i_tek_nar()
        except:
            CQT.msgbox(f'Не удалось проверить текущий наряд, попробуй еще')
            return
        if pnomer_nach == False:
            return

        #=======check==============
        zadanie = self.ui.textBrowser_zadanie.toPlainText()
        primech = self.ui.te_zamechain.toPlainText().strip()

        nom_nar = int(self.ui.lbl_nom_nar.text())
        tab = self.ui.tabWidget_2
        if self.check_dostupnosti_nar(nom_nar) == False:
            tab.setCurrentIndex(CQT.nom_tab_po_imen(tab, 'Доступные наряды'))
            self.zapoln_tabl_naryadov()

            CQT.msgbox('Наряд недоступен')
            return
        last_status_nar = CSQ.zapros(self.db_naryd,f"""SELECT Статус FROM jurnal WHERE Номер_наряда == {nom_nar} 
            and ФИО == "{CMS.ima_po_emp(self.glob_login)}" ORDER BY Пномер DESC LIMIT 1""")[-1][0]
        if last_status_nar != 'Начат':

            CQT.msgbox('Статус наряда не позволяет выполнить действие')
            return
        if vid_stop == 'Приостановлен':
            if primech == '' or len(primech) < 4:

                CQT.migat_obj(self,2,self.ui.te_zamechain,'Не указана причина паузы')
                return
        if not self.check_abstrakt(primech):
            return
        nom_mk = int(self.ui.lbl_nom_mk.text())
        now = F.now()
        #==========precalc_time==========
        date_diff = F.strtodate(F.now()) - F.strtodate(data_nach)
        poditog = round(date_diff.total_seconds()/60)
        poditog = 1 if poditog < 1 else poditog
        #==========установить время выполнения на строку начало==========
        zapros = f'UPDATE jurnal SET Подытог == ? WHERE Пномер == ?'
        param = [poditog,int(pnomer_nach)]
        try:
            CSQ.zapros(self.db_naryd, zapros,spisok_spiskov=param)
        except:

            CQT.msgbox(f'Ошибка занесения в Журнал')
            return
        #==================добавление новой строки паузы================
        shtamp = F.shtamp_from_date(now)
        stroka = [now, shtamp, nom_nar, CMS.ima_po_emp(self.glob_login), 0,
                  vid_stop, primech, '']




        CSQ.zapros(self.db_naryd, f"INSERT INTO jurnal "
                                      f"(Дата, Штамп, Номер_наряда,ФИО,Подытог,Статус,Примечание,Ном_заверш)"
                                      f" VALUES  (?,?,?,?,?,?,?,?)", spisok_spiskov=[stroka],
                       )
        check = CSQ.zapros(self.db_naryd, f"""SELECT Пномер FROM jurnal WHERE Штамп = '{shtamp}' and ФИО == '{CMS.ima_po_emp(self.glob_login)}'; """,one=True)
        if len(check) == 1:
            CQT.msgbox(f'Ошибка занесения в Журнал_3 попробуй позже')
            return

        if vid_stop == 'Завершен':
            zapros = f'''SELECT sum(Подытог) AS "Total Salary"
                          FROM jurnal
                         WHERE ФИО == "{CMS.ima_po_emp(self.glob_login)}" AND Статус == "Начат" 
                        AND Номер_наряда == {nom_nar}'''
            fact_vr = CSQ.zapros(self.db_naryd, zapros)[-1][0]
            fact_vr = int(fact_vr)

            new_name = CMS.ima_po_emp(self.glob_login)

            if self.DICT_EMPL_FULL[self.glob_fio]['Режим'] == 'Абстракт':
                new_name = primech
                zapros = f'UPDATE jurnal SET ФИО = "{new_name}" WHERE ФИО == "{CMS.ima_po_emp(self.glob_login)}" AND Номер_наряда == {nom_nar}'
                CSQ.zapros(self.db_naryd, zapros)
                print(f'Замена абстракта {CMS.ima_po_emp(self.glob_login)} на {new_name}')

            zapros = f'UPDATE naryad SET Фвремя = {fact_vr}, ФИО = "{new_name}" WHERE ФИО == "{CMS.ima_po_emp(self.glob_login)}" AND Пномер == {nom_nar}'
            CSQ.zapros(self.db_naryd, zapros)
            zapros = f'UPDATE naryad SET Фвремя2 == {fact_vr}, ФИО2 = "{new_name}" WHERE ФИО2 == "{CMS.ima_po_emp(self.glob_login)}" AND Пномер == {nom_nar}'
            CSQ.zapros(self.db_naryd, zapros)


            try:
                if "Исправление" in zadanie and 'Акт №' in zadanie:
                    tmp = zadanie.split('Акт №')
                    act = tmp[-1].split()[0]
                    if F.is_numeric(act):
                        zapros = f'''UPDATE act SET Наряд_исправления == {nom_nar}, Время_исправления == {fact_vr} WHERE Пномер == {int(act)}'''
                        CSQ.zapros(self.db_act,zapros)
            except:
                CQT.msgbox('Ошибка занесения отметки в акты о браке')
                return

            #====================Запись завершенных дсе===============
            zapros = f'''SELECT ДСЕ,Операции,Опер_колво,ДСЕ_ID,Внеплан FROM naryad WHERE Пномер == {nom_nar}'''
            query = CSQ.zapros(self.db_naryd, zapros)
            if query == False:

                CQT.msgbox(f'Не выполнена запись ДСЕ в МК')
                return
            if query[-1][4] == 0:

                res = CMS.load_res(nom_mk)


                spis_dse = query[-1][0].split('|')
                spis_oper = query[-1][1].split('|')
                spis_kolvo = query[-1][2].split('|')
                spis_id = query[-1][3].split('|')
                for i in range(len(spis_dse)):
                    dse_naim, dse_nn = spis_dse[i].split('$')
                    oper_nom, oper_naim = spis_oper[i].split('$')
                    kolvo = spis_kolvo[i]
                    id = spis_id[i]
                    flag_add = False
                    for j,res_dse in enumerate(res):
                        if res_dse['Наименование'] == dse_naim and res_dse['Номенклатурный_номер'] == dse_nn and id == str(res_dse['Номерпп']):
                            for k,oper in enumerate(res_dse['Операции']):
                                if oper['Опер_номер'] == oper_nom:
                                    if 'Закрыто,шт.' in oper:
                                        res[j]['Операции'][k]['Закрыто,шт.'] += int(kolvo)
                                    else:
                                        res[j]['Операции'][k]['Закрыто,шт.'] = int(kolvo)
                                    flag_add = True
                                    break
                        if flag_add:
                            break
                CMS.save_res(self.db_resxml,nom_mk,res)
                #========================================================
            self.zapoln_tabl_naryadov()

        self.clear_naryad_bar()

        CQT.msgbox(f'Наряд успешно {vid_stop}')
        #F.sleep(1)
        #=================================================
        #self.add_opoveshenie(vid_stop,nom_nar,nom_mk, self.glob_login.replace(',',' '),F.ochist_strok_pod_ima_fila(primech))



    @CQT.onerror
    def add_opoveshenie(self, vid_stop, nom_nar, nom_mk, fio, primech):#OFF
        zapros = f'''SELECT Номер_заказа, Номер_проекта, Вид FROM mk WHERE Пномер == {nom_mk}'''
        rez = CSQ.zapros(self.db_naryd,zapros)
        np = rez[-1][1]
        nz = rez[-1][0]
        vid = rez[-1][2]
        spis_opov = [F.now('%d.%m.%Y %H:%M:%S'), str(nom_nar), np + ' ' + nz, vid, fio, vid_stop,primech]
        F.dozapis_v_fail(F.scfg('Opoveshenie') + F.sep() + 'Opoveshenie_tgm.txt', spis_opov, True, sep='|')
        F.dozapis_v_fail(F.scfg('Opoveshenie') + F.sep() + 'Opoveshenie_tgm_arh.txt', spis_opov, True, sep='|')
        if self.ui.tbl_naryadi.rowCount() == 0:
            F.dozapis_v_fail(F.scfg('Opoveshenie') + F.sep() + 'Opoveshenie_tgm.txt',
                             f'{fio} остался без заданий. Уважаемые коллеги, пожалуйста примите меры!', True, sep='')
            F.dozapis_v_fail(F.scfg('Opoveshenie') + F.sep() + 'Opoveshenie_tgm_arh.txt',
                             f'{fio} остался без заданий. Уважаемые коллеги, пожалуйста примите меры!', True, sep='')


    @CQT.onerror
    def lbl_tek_narayd(self,fio):
        self.ui.lbl_tek_nar.setText('')
        rez = self.tekush_naruad(fio)
        if rez == False or rez == (False,False,False):
            return
        if rez == None:
            return
        if rez[0] == '':
            self.ui.lbl_tek_nar.setText('')
        else:
            self.ui.lbl_tek_nar.setText(str(rez[0]))


    @CQT.onerror
    def tekush_naruad(self,fio):
        zapros = f'''SELECT Номер_наряда, Пномер, Дата FROM jurnal WHERE ФИО == "{fio}" AND
                    Статус == "Начат" and  Подытог == 0'''
        rez = CSQ.zapros(self.db_naryd, zapros, shapka=False)
        if rez == False:

            CQT.msgbox(f'Бд занята пробуй позже')
            return False, False, False
        if rez == None:

            CQT.msgbox(f'Данные не получены')
            return False, False, False
        if len(rez) == 0:
            return ['','','']
        return rez[0]


app = QtWidgets.QApplication(sys.argv)
args = sys.argv[1:]
myappid = 'Powerz.BAG.SustControlWork.20.07.2021'  # !!!
QtWin.setCurrentProcessExplicitAppUserModelID(myappid)
app.setWindowIcon(QtGui.QIcon(os.path.join("icons", "tab.png")))

S = F.cfg['Stile'].split(",")
app.setStyle(S[0])
application = mywindow()
# ======================================================
versia = application.versia
if CMS.kontrol_ver(versia,"Выполнение2") == False:
    sys.exit()
# =========================================================
application.show()
sys.exit(app.exec())
#pyinstaller.exe --onefile --icon=Apathae.ico --noconsole Module.py
