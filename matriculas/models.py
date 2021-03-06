# -*- coding: utf-8 -*-

from django.db import models
from django.utils import timezone
import datetime

TZ = timezone.get_default_timezone()

# FIXME contar el numero de gente dentro segun el numero de plazas

TARIFAS = [
    # Esta formula es:
    #  precio = 0                            para -5 minutos
    #  precio = 0.50                         para 5-30 minutos
    #  precio = 0.491 + minutos / 60 * 0.515 para 30 minutos-6 horas
    #  precio = 4.80                         para 6-10 horas
    #  precio = 6.00                         para +10 horas
    (0, 0.00),
    (6, 0.50),
    (31, 0.60),
    (41, 0.80),
    (51, 0.90),
    (61, 1.00),
    (71, 1.10),
    (81, 1.20),
    (91, 1.30),
    (101, 1.40),
    (111, 1.50),
    (121, 1.60),
    (131, 1.65),
    (141, 1.70),
    (151, 1.80),
    (161, 1.90),
    (171, 2.00),
    (181, 2.10),
    (191, 2.15),
    (201, 2.20),
    (211, 2.30),
    (221, 2.40),
    (231, 2.50),
    (241, 2.60),
    (251, 2.65),
    (261, 2.70),
    (271, 2.80),
    (281, 2.90),
    (291, 3.00),
    (301, 3.10),
    (311, 3.15),
    (321, 3.20),
    (331, 3.30),
    (341, 3.40),
    (351, 3.50),
    (361, 4.80),
    (600, 6.00),
]


def get_tarifa(minutos):
    ultima_tarifa = 0.0
    for x, tarifa in TARIFAS:
        if x <= minutos:
            ultima_tarifa = tarifa
        else:
            return ultima_tarifa
    return ultima_tarifa


def get_month_range(year, month):
    start = datetime.datetime(year, month, 1, 0, 0)
    end = start + datetime.timedelta(days=32)
    end.replace(day=1, hour=0)
    return start, end


def get_day_range(year, month, day):
    if day <= 0:
        return get_month_range(year, month)
    else:
        start = datetime.datetime(year, month, day)
        end = start + datetime.timedelta(days=1)
        return timezone.make_aware(start, TZ), timezone.make_aware(end, TZ)


# Create your models here.
class Registro(models.Model):
    matricula = models.CharField(max_length=40)
    fecha_entrada = models.DateTimeField(default=timezone.now)
    fecha_salida = models.DateTimeField(blank=True, null=True)
    minutos = models.FloatField(blank=True, null=True)
    euros = models.FloatField(blank=True, null=True)
    usuario_entrada = models.CharField(max_length=40, blank=True, null=True)
    usuario_salida = models.CharField(max_length=40, blank=True, null=True)
    emitido_ticket = models.NullBooleanField()

    @property
    def hora_entrada(self):
        return self.fecha_entrada.strftime("%X") if self.fecha_entrada else None

    @property
    def hora_salida(self):
        return self.fecha_salida.strftime("%X") if self.fecha_salida else None

    def __unicode__(self):
        if not self.fecha_salida:
            return u"{} dentro desde las {}".format(self.matricula, self.hora_entrada)
        else:
            return u"{} salio a las {}".format(self.matricula, self.hora_salida)

    @staticmethod
    def coches_dia(year, month, day=None):
        start, end = get_day_range(year, month, day)
        return Registro.objects.filter(
            fecha_entrada__gte=start,
            fecha_entrada__lt=end
        )

    @staticmethod
    def estadisticas_dia(year, month, day):
        qs = Registro.coches_dia(year, month, day)
        total = qs.count()
        dentro = qs.filter(fecha_salida__isnull=True).count()
        recaudado = qs.aggregate(models.Sum('euros'))['euros__sum']
        return {
            'today': datetime.date(year, month, day),
            'coches_dentro': dentro,
            'coches_total': total,
            'coches_fuera': total - dentro,
            'total_recaudado': recaudado or 0.0,
        }

    @staticmethod
    def estadisticas_mes(year, month):
        qs_total = Registro.coches_dia(year, month)
        total_recaudado = 0.0
        out = []
        for i in range(1, 31):
            qs = qs_total.filter(fecha_entrada__day=i)
            total = qs.count()
            if total:
                dentro = qs.filter(fecha_salida__isnull=True).count()
                recaudado = qs.aggregate(models.Sum('euros'))['euros__sum'] or 0.0
                out.append({
                    'today': datetime.date(year, month, i),
                    'dia': i,
                    'coches_dentro': dentro,
                    'coches_total': total,
                    'coches_fuera': total - dentro,
                    'total_recaudado': recaudado,
                })
                total_recaudado += recaudado
        today = datetime.date.today()
        if today.year != year or today.month != month:
            today = datetime.date(year, month, 1)
        return {
            "today": today,
            "total_recaudado": total_recaudado,
            "data": out,
        }

    @staticmethod
    def matricula_entra(matricula, usuario=None):
        qs = Registro.objects.filter(
            matricula=matricula,
            fecha_salida__isnull=True)
        if qs.count() > 0:
            r = qs.get()
            usuario = "(por {})".format(r.usuario_entrada) if r.usuario_entrada else ""
            return u"La matricula '{}' ya esta dentro desde las {}!! {}".format(
                matricula, r.hora_entrada, usuario)
        else:
            r = Registro.objects.create(
                matricula=matricula,
                usuario_entrada=usuario,
                fecha_entrada=timezone.now())
            return u"Entrando matricula '{}' a las {}".format(
                matricula, r.hora_entrada)

    @staticmethod
    def matricula_renombra(matricula1, matricula2):
        qs = Registro.objects.filter(
            matricula=matricula1,
            fecha_salida__isnull=True)
        if qs.count() == 0:
            return u"No se encuentra la matricula {}".format(matricula1)
        else:
            r = qs.get()
            r.matricula = matricula2
            r.save()
            return u"Renombrada matricula {} a {} con exito".format(
                matricula1, matricula2)

    @staticmethod
    def matricula_sale(matricula, usuario=None):
        qs = Registro.objects.filter(
            matricula=matricula,
            fecha_salida__isnull=True)
        if qs.count() == 0:
            return u"La matricula '{}' no esta dentro!!".format(matricula)
        else:
            r = qs[0]
            r.fecha_salida = timezone.now()
            r.usuario_salida = usuario
            r.minutos = (r.fecha_salida - r.fecha_entrada).seconds/60.
            r.euros = get_tarifa(r.minutos)
            r.save()
            usuario = "(por {})".format(r.usuario_entrada) if r.usuario_entrada else ""
            return u"Saliendo matricula '{}' desde las {} {} hasta las {} y son {:.2f} €".format(
                matricula, r.hora_entrada, usuario, r.hora_salida, r.euros
            ).replace("  ", " ")

    class Meta:
        ordering = ["-fecha_entrada"]
