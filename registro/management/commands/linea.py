# -*- coding: utf-8 -*-

from optparse import make_option
from django.core.management.base import BaseCommand
from django.conf import settings
from registro.models import Registro
from django.utils import timezone

class Command(BaseCommand):

    help = u'Mete lo siguiente en base de datos: [entrar|salir] [matricula]'

    def handle(self, *args, **kwargs):
        if len(args) < 2:
            print "Linea de comandos:"
            print "- entra matricula:     e matricula [usuario]"
            print "- sale matricula:      s matricula [usuario]"
            print "- modifica matricula:  r matricula1 matricula2 (solo los que estan dentro)"
            return
        comando = matricula = usuario = None
        args = list(args)
        try:
            comando = args.pop(0).lower().strip()
            matricula = args.pop(0).lower().strip()
            usuario = args.pop(0).lower().strip()
        except IndexError as e:
            pass
        if comando == "e":
            out = Registro.matricula_entra(matricula, usuario)
        elif comando == "s":
            out = Registro.matricula_sale(matricula, usuario)
        elif comando == "r":
            out = Registro.matricula_renombra(matricula1, matricula2)
        else:
            out = "Comando '{}' no reconocido".format(comando)
        print out



