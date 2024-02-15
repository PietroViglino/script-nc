import netCDF4 
import os
import json
import csv
import numpy as np
import datetime as dt
import pytz

input_data_folder = 'input-folder'
destination_folder = 'output-folder'

def main(input_folder=os.getcwd(), destination_folder=os.getcwd()):
    for filename in os.listdir(input_folder):
        if filename.endswith('.csv'):
            with open(os.path.join(input_folder, filename), 'r') as csv_file:
                base_name = filename.replace('.csv', '')
                ncfile = netCDF4.Dataset(f'{destination_folder}/{base_name[:-6]}_{base_name[-6:]}.nc',mode='w',format='NETCDF4')
                depth_data = latitude_data = longitude_data = 0
                try:
                    with open(f'{input_folder}/{base_name}.json') as metadata:
                        parsed_json = json.load(metadata)
                        ncfile.institution = parsed_json['institution']
                        ncfile.wmo_platform_code = parsed_json['wmo_platform_code']
                        ncfile.site_name = parsed_json['site_name']
                        ncfile.title = parsed_json['title']
                        ncfile.institution_references = parsed_json['institution_references']
                        ncfile.contact = parsed_json['contact']
                        ncfile.author = parsed_json['author']
                        ncfile.data_assembly_center = parsed_json['data_assembly_center']
                        ncfile.pi_name = parsed_json['pi_name']
                        ncfile.distribution_statement = parsed_json['distribution_statement']
                        ncfile.citation = parsed_json['citation']
                        depth_data = parsed_json['depth']
                        latitude_data = parsed_json['latitude']
                        longitude_data = parsed_json['longitude']
                except:
                    print(f'No matching JSON file found for {base_name}')
                parsed_csv = list(csv.reader(csv_file))
                row = ncfile.createDimension('row', len(parsed_csv) - 1)
                time = ncfile.createVariable('time', 'f8', ('row',))
                time.shape = ("TIME",)
                time.long_name = "Valid Time GMT",
                time.standard_name = "time",
                time.units = "seconds since 1970-01-01T00:00:00Z",
                time.calendar = "Gregorian",
                time.axis = "T"
                conductivity = ncfile.createVariable('CNDC', 'f8', ('row',))
                conductivity.shape = ("TIME"),
                conductivity.standard_name = "sea_water_electrical_conductivity",
                conductivity.long_name = "electrical conductivity",
                conductivity.units = "S/m",
                conductivity.source_variable_name = "CNDC",
                conductivity.SDN = "SDN:P01::CNDCZZ01",
                conductivity.ep_parameter_group = "Water conductivity/ BioGeoChemical",
                conductivity.CMEMS = "CNDC"
                temp = ncfile.createVariable('TEMP', 'f8', ('row',))
                temp.shape = ("TIME"),
                temp.standard_name = "sea_water_temperature",
                temp.long_name = "sea temperature",
                temp.units = "degree_Celsius",
                temp.source_variable_name = "TEMP",
                temp.SDN = "SDN:P01::TEMPPR01",
                temp.ep_parameter_group = "Water Temperature",
                temp.CMEMS = "TEMP"
                pressure = ncfile.createVariable('PRES', 'f8', ('row',))
                pressure.shape = ("TIME"),
                pressure.standard_name = "sea_water_pressure",
                pressure.long_name = "Sea pressure",
                pressure.units = "dbar",
                pressure.axis = "Z"
                depth = ncfile.createVariable('DEPTH', 'f8', ('row'), compression='zlib')
                depth.shape = ("TIME")
                depth.units = 'm'
                depth.standard_name = "depth",
                depth.long_name ="Depth",
                depth.axis = "Z"
                latitude = ncfile.createVariable('LATITUDE', 'f8', ('row'), compression='zlib')
                latitude.shape = ("TIME"),
                latitude.standard_name = "latitude",
                latitude.long_name ="Latitude",
                latitude.units = "degrees_north"
                latitude.axis = "Y",
                latitude.reference_datum = "geographical coordinates, WGS84 projection",
                latitude.valid_min = np.float32(-90.0),
                latitude.valid_max = np.float32( 90.0)
                longitude = ncfile.createVariable('LONGITUDE', 'f8', ('row'), compression='zlib')
                longitude.shape = ("TIME"),
                longitude.standard_name = "longitude",
                longitude.long_name = "Longitude",
                longitude.units = "degrees_east",
                longitude.axis = "X",
                longitude.reference_datum = "geographical coordinates, WGS84 projection",
                longitude.valid_min = np.float32(-180.0),
                longitude.valid_max =np.float32( 180.0)
                time_data = []
                conductivities_data = []
                temperatures_data = []
                pressures_data = []
                for row in parsed_csv[1:]:
                    # timezone adjustment?
                    # parsed_time = dt.datetime.fromisoformat(row[0]).astimezone(dt.timezone.utc)
                    parsed_time = dt.datetime.fromisoformat(row[0]) 
                    time_data.append(parsed_time.timestamp())
                    conductivities_data.append(row[1])
                    temperatures_data.append(row[2])
                    pressures_data.append(row[3])
                time[:] = np.array(time_data)
                conductivity[:] = np.array(conductivities_data)
                temp[:] = np.array(temperatures_data)
                pressure[:] = np.array(pressures_data)
                depth[:] = np.full(len(parsed_csv) - 1, depth_data)
                latitude[:] = np.full(len(parsed_csv) - 1, latitude_data)
                longitude[:] = np.full(len(parsed_csv) - 1, longitude_data)
                ncfile.close()

if __name__ == '__main__':
    main(input_data_folder, destination_folder)