# -*- coding: UTF-8 -*-
#sindientes.py
from sugar.activity import activity
import gtk
import logging
from gettext import gettext as _
from os.path import exists
from datetime import datetime
import pickle
import utils

_logger = logging.getLogger('ahorcado-activity')
_logger.setLevel(logging.DEBUG)

class SinDientes(activity.Activity):

    def __init__(self, handle):
        super(SinDientes, self).__init__(handle)
        #ventana
        #self.ventana = gtk.Window()
        #self.ventana.set_title(_('Ahorcado'))
        self.set_title(_('Sin Dientes'))
        self.connect('key-press-event', self._key_press_cb)
        self.connect('destroy', self._destroy_cb)

        #Barra de herramientas sugar
        barra_herramientas = activity.ActivityToolbox(self)
        self.set_toolbox(barra_herramientas)
        barra_herramientas.show()

        #contenedores
        self.contenedor = gtk.VBox()
        #self.ventana.add(self.contenedor)


        self.contenedor_superior = gtk.HBox()
        self.contenedor_inferior= gtk.HBox()
        
        self.contenedor.pack_start(self.contenedor_superior)
        self.contenedor.pack_start(self.contenedor_inferior, expand=False)

        """self.contenedor_puntaje = gtk.VBox()#desde aca lleva interface de los tres mejores puntajes
        self.primero_label = gtk.Label("Primer Puntaje : " % load_puntaje())
        self.contenedor_puntaje.pack_start(self.primero_label, False, False, 0)"""

        self.subcontenedor= gtk.VBox()
                
        #interface
        self.imagen = gtk.Image()
        self.instrucciones_label = gtk.Label(_('Instrucciones'))
        self.instrucciones_label.set_justify(gtk.JUSTIFY_FILL)
        self.instrucciones_label.set_line_wrap(gtk.TRUE)
        self.aciertos_label = gtk.Label('Puntaje: 0')
        self.errores_label = gtk.Label()
        self.palabra_label = gtk.Label()
        self.letrasusadas_label = gtk.Label(_('Letras Usadas: '))
        self.palabra_entry = gtk.Entry()
        self.ok_btn = gtk.Button(_('Ok'))
        self.ok_btn.connect('clicked', self._ok_btn_clicked_cb, None)
        self.nuevojuego_btn = gtk.Button(_('Nuevo Juego'))
        self.nuevojuego_btn.connect('clicked', self._nuevojuego_btn_clicked_cb, None)
        self._cambiar_imagen(0)

        self.aciertos = 0 #Cuenta los aciertos de letras en la palabra secreta
        self.lista_record = self.load_puntaje()
        self._leer_diario() # Crea las variables necesarias para el comienzo del juego

        #agregando elementos
        self.contenedor_superior.pack_start(self.imagen)
        self.contenedor_superior.pack_start(self.subcontenedor)
        self.subcontenedor.pack_start(self.instrucciones_label)
        self.subcontenedor.pack_start(self.aciertos_label)
        self.subcontenedor.pack_start(self.letrasusadas_label)
        self.subcontenedor.pack_start(self.errores_label)
        self.subcontenedor.pack_start(self.palabra_label)
        self.subcontenedor.pack_start(self.nuevojuego_btn)

        self.contenedor_inferior.pack_start(self.palabra_entry)
        self.contenedor_inferior.pack_start(self.ok_btn, False)
        
        self.contenedor.show_all()
        self.nuevojuego_btn.hide()
        self.set_canvas(self.contenedor)
        self.show()

    def _creacion(self, nuevo=True):
        '''Crea las variables necesarias para el comienzo del juego'''
        if nuevo:
            self.palabra, self.significado = utils.palabra_aleatoria()
            self.l_aciertos = []
            self.l_errores= []
            self.errores = 0
            self._cambiar_imagen(0)
        else:
            self._cambiar_imagen(self.errores)
        
        self._actualizar_labels('Instrucciones')
        self.nuevojuego_btn.hide()

    def _ok_btn_clicked_cb(self, widget, data=None):
        self._actualizar_palabra()

    def _nuevojuego_btn_clicked_cb(self, widget, data=None):
        self.palabra_entry.set_sensitive(True) #Activa la caja de texto
        self.ok_btn.set_sensitive(True) #Activa el botón ok
        self._creacion()
        
    def _cambiar_imagen(self, level):
        ruta = 'resources/%s.png' % level
        _logger.debug('level: %s' % level)
        self.imagen.set_from_file(ruta)

    def _key_press_cb(self, widget, event):
        keyname = gtk.gdk.keyval_name(event.keyval)
        _logger.debug('keyname: %s' % keyname)
        if keyname == 'Return' or keyname == "KP_Enter":
            
            self._actualizar_palabra()
        return False

    def read_file(self, filepath):
        pass

    def write_file(self, filepath):
        pass

    def main(self):
        gtk.main()

    def load_puntaje(self):
        if exists("puntaje.pck"):
            f_read = open("puntaje.pck", "rb")
            x = pickle.load(f_read)
            f_read.close()
            return x
        else:
            return []

    def guardar_puntaje(self):
        f_write = open("puntaje.pck", "ab")
        info_gamer = (self.aciertos, datetime.now())
        lista_gamer = []
        lista_gamer.append(info_gamer)
        pickle.dump(lista_gamer, f_write)
        f_write.close()

    def _destroy_cb(self, widget, data=None):
        self.guardar_puntaje()
        gtk.main_quit()

    def _actualizar_palabra(self):

        #Convierte la letra a minuscula
        letra_actual = self.palabra_entry.get_text().lower()
        _logger.debug('letra_actual: %s' % letra_actual)

        #Evalua si se escribio mas de 1 letra o esta vacio
        if (len(letra_actual) is not 1 or letra_actual == " "): 
            self.palabra_entry.set_text('')
            _logger.debug('mas de una letra o vacio')
            self.instrucciones_label.set_text(_("Instrucciones:\nIntroduzca solo una letra!"))
        
        #Evalua si letra esta dentro de palabra
        elif (letra_actual in self.palabra and letra_actual not in self.l_aciertos):
            self.l_aciertos.append(letra_actual)
            
            for i in range(len(self.palabra)):
                if (letra_actual == self.palabra[i]):
                    self.aciertos += 1
            
            _logger.debug('letra dentro de palabra, aciertos: %s, errores: %s' %(self.aciertos, self.errores))
            self._actualizar_labels("Instrucciones:\nLetra dentro de palabra secreta!")
            
            #Evalua si se acerto la palabra y temina el juego
            if (self.aciertos == len(self.palabra)): 
                _logger.debug('acerto palabra')
                self.instrucciones_label.set_text(_('Instrucciones:\nAcertastes la palabra secreta, ' \
                                                    'FELICIDADES! \n su significado es: %s' % self.significado))
                self.nuevojuego_btn.show() # muestra el boton para comenzar el juego

        #Evalua si letra es repetida y esta dentro de palabra
        elif (letra_actual in self.palabra and letra_actual in self.l_aciertos): 
            _logger.debug('letra repetida y dentro de palabra, aciertos: %s, errores: %s' %(self.aciertos, self.errores))
            self._actualizar_labels("Instrucciones:\nLetra repetida y dentro de palabra secreta!")

        #Evalua si letra no esta dentro de palabra
        elif (letra_actual not in self.palabra and letra_actual not in self.l_errores):
            self.l_errores.append(letra_actual)
            self.errores += 1
            self._cambiar_imagen(self.errores)
            _logger.debug('letra fuera de palabra, aciertos: %s, errores: %s' %(self.aciertos, self.errores))
            self._actualizar_labels("Instrucciones:\nLetra fuera de palabra secreta!")
            
            #Evalua si se completo el ahorcado y temina el juego            
            if (self.errores >= 8):
                _logger.debug('fin del juego')
                self.instrucciones_label.set_text(_('Instrucciones:\nLa palabra secreta era %s, ' \
                                                    'Fin del juego! x( su significado es %s' % 
                                                    (self.palabra, self.significado)) )
                self.aciertos = 0
                self.palabra_entry.set_sensitive(False) #Activa la caja de texto
                self.ok_btn.set_sensitive(False) #Inactiva el botón ok una vez que pierde
                self.nuevojuego_btn.show() # muestra el boton para comenzar el juego

        #Evalua si letra es repetida y no dentro de palabra
        elif (letra_actual not in self.palabra and letra_actual in self.l_errores): 
            _logger.debug('letra repetida y fuera de palabra, aciertos: %s, errores: %s' %(self.aciertos, self.errores))
            self._actualizar_labels("Instrucciones:\nLetra repetida y fuera de palabra secreta!")

        self._pintar_palabra()
        
    def _actualizar_labels(self, instrucciones):
        '''Actualiza labels segun instrucciones'''
        self.palabra_entry.set_text('')
        self.instrucciones_label.set_text(_(instrucciones))
        self.aciertos_label.set_text(_('Puntaje: %s' % self.aciertos))
        letras = ', '.join(letra for letra in self.l_aciertos)
        letras2 = ', '.join(letra for letra in self.l_errores)
        self.letrasusadas_label.set_text(_('Letras Usadas: %s %s' % (letras,letras2)))
        self.errores_label.set_text(_('Errores: %s' % self.errores))

    def _pintar_palabra(self):
        '''Pinta las lineas de la palabra'''
        pista = ''
        for letra in self.palabra:
            if letra in self.l_aciertos:
                pista += '%s ' % letra
            else:
                pista += '_ '
        self.palabra_label.set_text(pista)

    def _leer_diario(self):
        try:
            self.aciertos = int(self.metadata['aciertos'])
            self.palabra = str(self.metadata['palabra'])
            self.l_aciertos = str(self.metadata['l_aciertos'])
            self.l_errores = str(self.metadata['l_errores'])
            self._creacion(False)
        except:
            self._creacion(True)

    def read_file(self, filepath):
        _logger.debug('leyendo desde  %s' % filepath)
        if exists(filepath):
            f_read = open(filepath, "rb")
            x = pickle.load(f_read)
            f_read.close()
            return x
        else:
            return []

    def write_file(self, filepath):
        _logger.debug('Guardando en: %s' % filepath)
        self.metadata['aciertos'] = self.aciertos
        self.metadata['palabra'] = self.palabra
        self.metadata['l_aciertos'] = self.l_aciertos
        self.metadata['l_errores'] = self.l_errores
        self.metadata['mime_type'] = 'application/x-sindientes'

        f_write = open(filepath, "ab")
        info_gamer = (self.aciertos, datetime.now())
        lista_gamer = []
        lista_gamer.append(info_gamer)
        pickle.dump(lista_gamer, f_write)
        f_write.close()
