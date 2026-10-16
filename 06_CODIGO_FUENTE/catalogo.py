"""Catálogo de requisitos trazable. Geometría simbólica: no dimensiona instalaciones."""
from dataclasses import dataclass, field, asdict


@dataclass
class Simbolo:
    nombre: str
    codigo: str
    descripcion: str
    sistema: str
    familia: str
    capa: str
    forma: str
    montaje: str = 'POR DEFINIR'
    datos: dict = field(default_factory=dict)
    fuente: str = 'Prompt del usuario; convencion grafica interna de proyecto'

    def atributos(self):
        result = dict(CODIGO=self.codigo, TIPO=self.codigo, DESCRIPCION=self.descripcion, SISTEMA=self.sistema,
                      MONTAJE=self.montaje, ALTURA='', TABLERO='', CIRCUITO='', OBSERVACIONES='',
                      NORMA='CONVENCION DE PROYECTO - COTEJO NORMATIVO PENDIENTE')
        result.update(self.datos)
        return result


def catalogo():
    r = []

    def add(nombre, codigo, descripcion, sistema, familia, capa, forma, montaje='POR DEFINIR', **datos):
        r.append(Simbolo(nombre, codigo, descripcion, sistema, familia, capa, forma, montaje, datos))

    for n, desc, forma, montaje, data in [
        ('01', 'LED lineal hermetica IP65', 'luz_lineal', 'POR CONFIRMAR', {'IP': 'IP65', 'DIM_FISICA': ''}),
        ('02', 'Aplique circular de pared IP65', 'luz_aplique', 'PARED', {'IP': 'IP65', 'DIM_FISICA': ''}),
        ('03', 'Panel LED nominal 600 x 600 mm', 'luz_panel', 'EMPOTRADO', {'DIM_FISICA': '600x600 mm'}),
        ('04', 'Downlight LED empotrado', 'luz_downlight', 'EMPOTRADO', {'DIM_FISICA': ''}),
    ]:
        add('IE_L'+n, 'L-'+n, desc, 'IE', '01_ILUMINACION_CONTROLES', 'IE-LUMINARIAS', forma,
            montaje, POTENCIA='', **data)
    controls = [
        ('SIMPLE', 'IS', 'Interruptor simple', 'control_1'),
        ('DOBLE', 'ID', 'Interruptor doble', 'control_2'),
        ('TRIPLE', 'IT', 'Interruptor triple', 'control_3'),
        ('CONMUTACION', 'IC', 'Interruptor de conmutacion', 'control_conmuta'),
        ('CRUCE', 'IX', 'Interruptor de cruce', 'control_cruce'),
        ('PULSADOR', 'PU', 'Pulsador', 'pulsador'),
        ('MOVIMIENTO', 'SM', 'Sensor de movimiento', 'sensor_movimiento'),
        ('PRESENCIA', 'SP', 'Sensor de presencia', 'sensor_presencia'),
        ('REGULADOR', 'CI', 'Control / regulador de iluminacion', 'regulador'),
    ]
    for n, code, desc, shape in controls:
        add('IE_'+n, code, desc, 'IE', '01_ILUMINACION_CONTROLES', 'IE-INTERRUPTORES', shape)
    normal = [
        ('M040', 'TN1', 'Doble 220 V 2P+T - pared 0.40 m', 'pared', 'PARED', '+0.40 m'),
        ('M120', 'TN2', 'Doble 220 V 2P+T - pared 1.20 m', 'pared', 'PARED', '+1.20 m'),
        ('EST110', 'TN3', 'Doble 220 V 2P+T - estanco 1.10 m', 'estanco', 'PARED', '+1.10 m'),
        ('PISO', 'TN4', 'Doble 220 V 2P+T - piso', 'piso', 'PISO', 'NPT +/-0.00'),
        ('MES110', 'TN5', 'Doble 220 V 2P+T - mesada 1.10 m', 'mesada', 'MESADA', '+1.10 m'),
        ('MES120', 'TN6', 'Doble 220 V 2P+T - mesada 1.20 m', 'mesada', 'MESADA', '+1.20 m'),
        ('TECHO', 'TN7', 'Doble 220 V 2P+T - techo', 'techo', 'TECHO', ''),
    ]
    stabilized = [
        ('M040', 'TE1', 'Doble estabilizado - pared 0.40 m', 'pared', 'PARED', '+0.40 m'),
        ('M120', 'TE2', 'Doble estabilizado - pared 1.20 m', 'pared', 'PARED', '+1.20 m'),
        ('PISO', 'TE3', 'Doble estabilizado - piso', 'piso', 'PISO', 'NPT +/-0.00'),
        ('AVTECHO', 'TE4', 'Estabilizado audiovisual - techo', 'techo', 'TECHO', ''),
        ('AV220', 'TE5', 'Estabilizado para pantalla - 2.20 m', 'pared', 'PARED', '+2.20 m'),
        ('AV120', 'TE6', 'Estabilizado para dispensador - 1.20 m', 'pared', 'PARED', '+1.20 m'),
        ('ESPECIAL', 'TE7', 'Salida estabilizada dedicada', 'dedicado', 'POR DEFINIR', ''),
    ]
    for prefix, rows, capa, power in [('TN', normal, 'IE-TOMAS-NORMALES', 'NORMAL'),
                                       ('TE', stabilized, 'IE-TOMAS-ESTABILIZADOS', 'ESTABILIZADO')]:
        for n, code, desc, shape, mount, height in rows:
            add('IE_'+prefix+'_'+n, code, desc, 'IE', '02_TOMACORRIENTES_FUERZA', capa,
                'toma_'+shape+('_est' if prefix == 'TE' else ''), mount,
                ALTURA=height, TENSION='220 V', CONFIGURACION='2P+T', ALIMENTACION=power,
                CORRIENTE='', IP='')
    for name, code, desc, shape in [('FUERZA', 'FZ1', 'Salida de fuerza dedicada', 'fuerza'),
                                   ('MECANICA', 'FM1', 'Salida para equipo mecanico', 'mecanica')]:
        add('IE_'+name, code, desc, 'IE', '02_TOMACORRIENTES_FUERZA', 'IE-FUERZA', shape,
            TENSION='', FASES='', POTENCIA='', EQUIPO='')
    for name, code, desc, mount in [
        ('ILUMINACION', 'CI1', 'Caja de paso de iluminacion', 'POR DEFINIR'),
        ('TOMAS', 'CT1', 'Caja de paso de tomacorrientes', 'POR DEFINIR'),
        ('FUERZA', 'CF1', 'Caja de paso de fuerza', 'POR DEFINIR'),
        ('DERIVACION', 'CD1', 'Caja de derivacion', 'POR DEFINIR'),
        ('PARED', 'CP1', 'Caja de paso en pared', 'PARED'),
        ('TECHO', 'CC1', 'Caja de paso en techo', 'TECHO'),
        ('ESPECIAL', 'CE1', 'Caja para canalizacion especial', 'POR DEFINIR'),
    ]:
        add('IE_CAJA_'+name, code, desc, 'IE', '03_CAJAS_TABLEROS_CIRCUITOS', 'IE-CAJAS-PASO',
            'caja_rect' if name == 'ESPECIAL' else 'caja', mount,
            DIMENSIONES='', MATERIAL='', IP='', FUNCION=name)
    for n, code, desc in [('GENERAL','TG1','Tablero general'), ('DISTRIBUCION','TD1','Tablero de distribucion'),
                          ('UPS','UPS1','Alimentacion ininterrumpida / UPS')]:
        add('IE_TABLERO_'+n, code, desc, 'IE', '03_CAJAS_TABLEROS_CIRCUITOS', 'IE-TABLERO',
            'tablero_'+n.lower(), 'POR DEFINIR', TENSION='', POTENCIA='', CORRIENTE='')
    for n, code, desc, shape in [('SUBE','SB','Canalizacion que sube','sube'),
                                ('BAJA','BJ','Canalizacion que baja','baja'),
                                ('SUBE_BAJA','S/B','Canalizacion que sube y baja','sube_baja'),
                                ('TIERRA','PT','Punto de puesta a tierra','tierra'),
                                ('CIRCUITO','C01','Identificador de circuito','circuito')]:
        add('IE_'+n, code, desc, 'IE', '03_CAJAS_TABLEROS_CIRCUITOS', 'IE-CODIGOS', shape)
    comms = [
        ('DATA_SIMPLE','D1','Salida simple de data RJ45','IC-DATA','data_1','PARED',{'PUERTOS':'1','CATEGORIA':''}),
        ('DATA_DOBLE','D2','Salida doble Cat 6A - 2 RJ45','IC-DATA','data_2','PARED',{'PUERTOS':'2','CATEGORIA':'CAT 6A'}),
        ('VOZ','V1','Salida de voz','IC-VOZ','voz','PARED',{'PUERTOS':'1'}),
        ('VOZ_DATA','VD1','Salida combinada voz / data','IC-VOZ','voz_data','PARED',{'PUERTOS':'2'}),
        ('AP','AP1','Punto de acceso Wi-Fi','IC-WIFI','ap','POR DEFINIR',{}),
        ('CAM_DOMO','CD1','Camara CCTV tipo domo','IC-CCTV','cam_domo','TECHO',{}),
        ('CAM_BALA','CB1','Camara CCTV tipo bala','IC-CCTV','cam_bala','PARED',{}),
        ('CAM_PTZ','CZ1','Camara CCTV tipo PTZ','IC-CCTV','cam_ptz','POR DEFINIR',{}),
        ('CONTROL_ACCESO','CA1','Punto de control de acceso','IC-ACCESOS','acceso','POR DEFINIR',{}),
        ('LECTOR','LT1','Lector de tarjetas','IC-ACCESOS','lector','PARED',{}),
        ('CERRADURA','EM1','Cerradura electromagnetica','IC-ACCESOS','cerradura','PUERTA',{}),
        ('PULSADOR','PS1','Pulsador de salida','IC-ACCESOS','pulsador_salida','PARED',{}),
        ('RACK','RK1','Rack de comunicaciones','IC-RACK','rack','POR DEFINIR',{'UNIDADES_RACK':'','DIMENSIONES':''}),
        ('GABINETE','GC1','Gabinete de comunicaciones','IC-RACK','gabinete','POR DEFINIR',{'DIMENSIONES':''}),
        ('PATCH_PANEL','PP1','Patch panel','IC-RACK','patch','RACK',{'PUERTOS':''}),
        ('SWITCH','SW1','Switch de comunicaciones','IC-RACK','switch','RACK',{'PUERTOS':'','POE':''}),
        ('CAJA','CC1','Caja de paso de comunicaciones','IC-CAJAS','caja','POR DEFINIR',{'DIMENSIONES':'','MATERIAL':''}),
        ('FO_SALIDA','FO1','Salida de fibra optica','IC-FIBRA','fibra','POR DEFINIR',{'FIBRAS':'','CONECTOR':''}),
        ('FO_INTERCONEXION','FI1','Interconexion de fibra optica','IC-FIBRA','fibra_interconexion','POR DEFINIR',{'FIBRAS':''}),
    ]
    for n, code, desc, layer, shape, mount, data in comms:
        add('IC_'+n, code, desc, 'IC', '04_DATA_COMUNICACIONES', layer, shape, mount,
            PUNTO='', CABLE='', **data)
    fire = [
        ('HUMO','DH1','Detector de humo','DACI-HUMO','detector_humo','TECHO'),
        ('TERMICO','DT1','Detector termico','DACI-TERMICO','detector_termico','TECHO'),
        ('MULTICRITERIO','DM1','Detector multicriterio','DACI-HUMO','detector_multi','TECHO'),
        ('DUCTO','DD1','Detector de humo para ductos','DACI-HUMO','detector_ducto','DUCTO'),
        ('ESTACION','EM1','Estacion manual de alarma','DACI-ESTACIONES','estacion','PARED'),
        ('SIRENA','SA1','Sirena de alarma','DACI-SIRENAS','sirena','POR DEFINIR'),
        ('ESTROBO','LE1','Luz estroboscopica','DACI-SIRENAS','estrobo','POR DEFINIR'),
        ('SIRENA_ESTROBO','SE1','Sirena con luz estroboscopica','DACI-SIRENAS','sirena_estrobo','POR DEFINIR'),
        ('FACP','FACP1','Panel central de alarma / FACP','DACI-PANELES','facp','PARED'),
        ('REPETIDOR','PR1','Panel repetidor','DACI-PANELES','repetidor','PARED'),
        ('MONITOREO','MM1','Modulo de monitoreo','DACI-MODULOS','modulo_monitoreo','POR DEFINIR'),
        ('CONTROL','MC1','Modulo de control','DACI-MODULOS','modulo_control','POR DEFINIR'),
        ('AISLADOR','AI1','Modulo aislador','DACI-MODULOS','modulo_aislador','POR DEFINIR'),
        ('FUENTE','FA1','Fuente auxiliar de alimentacion','DACI-MODULOS','fuente','POR DEFINIR'),
        ('CAJA','CA1','Caja de paso DACI','DACI-CAJAS','caja','POR DEFINIR'),
        ('INTERFAZ','IF1','Interfaz de supervision / control','DACI-MODULOS','interfaz','POR DEFINIR'),
    ]
    for n, code, desc, layer, shape, mount in fire:
        add('DACI_'+n, code, desc, 'DACI', '05_DETECCION_ALARMA', layer, shape, mount,
            LAZO='', DIRECCION='', ZONA='', MODELO='', DIMENSIONES='' if n == 'CAJA' else '')
    from norma_dge import aplicar
    return aplicar(r,add)


CAPAS = {
    'IE-LUMINARIAS': (7,25), 'IE-ILUMINACION-CIRCUITOS': (2,18), 'IE-INTERRUPTORES': (7,18),
    'IE-TOMAS-NORMALES': (7,25), 'IE-TOMAS-ESTABILIZADOS': (1,25), 'IE-FUERZA': (1,30),
    'IE-CAJAS-PASO': (7,25), 'IE-TUBERIA-EMT': (4,18), 'IE-TUBERIA-PVC': (3,18),
    'IE-TUBERIA-CORRUGADA': (6,18), 'IE-TUBERIA-FMC': (2,18), 'IE-TABLERO': (7,35),
    'IE-TEXTOS': (7,18), 'IE-CODIGOS': (7,18), 'IE-COTAS': (8,13), 'IE-LEYENDA': (7,18),
    'IC-DATA': (4,25), 'IC-VOZ': (4,25), 'IC-WIFI': (4,25), 'IC-CCTV': (5,25),
    'IC-ACCESOS': (6,25), 'IC-RACK': (4,30), 'IC-FIBRA': (3,25),
    'IC-CANALIZACIONES': (4,18), 'IC-CAJAS': (4,25), 'IC-TEXTOS': (7,18),
    'DACI-HUMO': (1,25), 'DACI-TERMICO': (1,25), 'DACI-ESTACIONES': (1,25),
    'DACI-SIRENAS': (1,25), 'DACI-PANELES': (1,35), 'DACI-MODULOS': (1,25),
    'DACI-SLC': (1,18), 'DACI-NAC': (6,18), 'DACI-CANALIZACIONES': (1,18),
    'DACI-CAJAS': (1,25), 'DACI-TEXTOS': (7,18), 'DACI-ALIMENTACION': (2,18),
    'DACI-SUPERVISION': (3,18), 'ARQ-REFERENCIA': (8,13),
    'EIC-CATALOGO': (7,18), 'EIC-MARCO': (8,13), 'VIEWPORTS': (8,0),
}


def rutas():
    result = []
    for material in ('EMT','PVC','CORR','FMC'):
        for diametro in (16,20,25,32,40,50):
            layer = {'EMT':'IE-TUBERIA-EMT','PVC':'IE-TUBERIA-PVC',
                     'CORR':'IE-TUBERIA-CORRUGADA','FMC':'IE-TUBERIA-FMC'}[material]
            result.append(dict(nombre=f'EIC_{material}_D{diametro}', texto=f'{material} %%c{diametro} mm',
                               capa=layer, sistema='IE', material=material, diametro=diametro))
    for name, text, layer, system in [
        ('CAT6A_UFTP','U/FTP CAT6A','IC-CANALIZACIONES','IC'),
        ('CAT6A_FUTP','F/UTP CAT6A','IC-CANALIZACIONES','IC'),
        ('FIBRA','FO','IC-FIBRA','IC'), ('BANDEJA','BANDEJA COM','IC-CANALIZACIONES','IC'),
        ('CCTV','CCTV','IC-CCTV','IC'), ('ACCESO','ACCESO','IC-ACCESOS','IC'),
        ('IC_EMT','COM EMT','IC-CANALIZACIONES','IC'),
        ('IC_PVC','COM PVC','IC-CANALIZACIONES','IC'),
        ('IC_CORR','COM CORR','IC-CANALIZACIONES','IC'),
        ('SLC','SLC','DACI-SLC','DACI'), ('NAC','NAC','DACI-NAC','DACI'),
        ('ALIM','ALIM DACI','DACI-ALIMENTACION','DACI'),
        ('SUPERVISION','SUP DACI','DACI-SUPERVISION','DACI'),
        ('MODULOS','MOD DACI','DACI-CANALIZACIONES','DACI'),
        ('PANELES','RED FACP','DACI-CANALIZACIONES','DACI'),
        ('DACI_EMT','DACI EMT','DACI-CANALIZACIONES','DACI'),
        ('DACI_PVC','DACI PVC','DACI-CANALIZACIONES','DACI'),
        ('DACI_CORR','DACI CORR','DACI-CANALIZACIONES','DACI'),
    ]:
        result.append(dict(nombre='EIC_'+name,texto=text,capa=layer,sistema=system,material='',diametro=''))
    return result
