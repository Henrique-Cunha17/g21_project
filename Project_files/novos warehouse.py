import csv
import random

# Dicionário de warehouse_id para cidade
warehouse_id_to_city = {
    10: 'Lisboa',
    23: 'Porto',
    20: 'Aveiro',
    25: 'Valongo',
    17: 'Coimbra',
    8: 'Faro',
    21: 'Sintra',
    12: 'Vila Real',
    27: 'Marinha Grande',
    3: 'Covilhã',
    19: 'Matosinhos',
    13: 'Espinho',
    22: 'Ponte de Lima',
    14: 'Braga',
    29: 'Guimarães',
    7: 'Famalicão',
    4: 'Águeda',
    11: 'Elvas',
    26: 'Odemira',
    24: 'Sines',
    2: 'Palmela',
    28: 'Vila Franca de Xira',
    5: 'Portalegre',
    15: 'Bragança',
    30: 'Oeiras',
    6: 'Viseu',
    18: 'Golegã',
    1: 'Murtosa'
}

# Dicionário de warehouse_id para coordenadas (latitude, longitude)
warehouse_id_to_coords = {
    10: (38.722252, -9.139337),
    23: (41.157944, -8.629105),
    20: (40.640505, -8.653754),
    25: (41.195999, -8.495800),
    17: (40.203314, -8.410257),
    8:  (37.017963, -7.930834),
    21: (38.802868, -9.381659),
    12: (41.300621, -7.744129),
    27: (39.750000, -8.933333),
    3:  (40.286011, -7.504530),
    19: (41.182836, -8.689084),
    13: (41.007599, -8.641400),
    22: (41.767368, -8.583160),
    14: (41.545448, -8.426507),
    29: (41.444858, -8.296193),
    7:  (41.410328, -8.519728),
    4:  (40.577801, -8.444420),
    11: (38.881153, -7.162814),
    26: (37.598801, -8.645540),
    24: (37.956081, -8.868890),
    2:  (38.569801, -8.901930),
    28: (38.955601, -8.989230),
    5:  (39.293800, -7.428880),
    15: (41.806439, -6.756742),
    30: (38.697948, -9.316354),
    6:  (40.661011, -7.909710),
    18: (39.404999, -8.486000),
    1:  (40.748349, -8.651919)
}

city_list = list(warehouse_id_to_city.values())

input_file = r'Project_files\G21_Logistics – Shipments  Carriers with Warehouses_merged.csv'
output_file = r'Project_files\G21_Logistics_corrigido.csv'

with open(input_file, newline='', encoding='utf-8') as infile, \
     open(output_file, 'w', newline='', encoding='utf-8') as outfile:
    reader = csv.reader(infile)
    header = next(reader)
    # Adiciona as novas colunas ao header
    header += ['latitude', 'longitude']
    writer = csv.writer(outfile)
    writer.writerow(header)
    for row in reader:
        warehouse_id = int(row[10])
        city = warehouse_id_to_city.get(warehouse_id)
        coords = warehouse_id_to_coords.get(warehouse_id, (None, None))
        if city:
            # Substitui origin (coluna 4)
            row[4] = city
            # Destination: valor aleatório diferente do origin
            dest_city = random.choice([c for c in city_list if c != city])
            row[5] = dest_city
            # Substitui location (penúltima coluna)
            row[-2] = city
        # Adiciona latitude e longitude ao fim da linha
        row += [coords[0], coords[1]]
        writer.writerow(row)

print("Ficheiro corrigido criado:", output_file)