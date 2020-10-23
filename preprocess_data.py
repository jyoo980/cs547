import pandas as pd
import numpy as np

provincial_codes = ['CA-AB', ]

def main(country_region_code='CA'):
    print('Start Processing')
    df = pd.read_csv('Global_Mobility_Report.csv')
    all_keys = df.keys()
    print(all_keys)
    all_countries = df['country_region_code']
    print(all_countries)
    selected_country = df.loc[df['country_region_code'] == country_region_code]
    
    selected_country.to_csv('canada_data.csv')

    selected_country['iso_3166_2_code'].fillna(0, inplace=True)
    provinal_data = selected_country.loc[selected_country['iso_3166_2_code'] != 0]

    provinal_data.to_csv('provincal_data.csv')

    bc_overall_data = provinal_data.loc[provinal_data['sub_region_1']=='British Columbia']
    bc_overall_data.to_csv('bc_province_data.csv')

    provicial_local_data = selected_country.loc[selected_country['iso_3166_2_code'] == 0]
    bc_local_data = provicial_local_data.loc[provicial_local_data['sub_region_1'] == 'British Columbia']
    bc_local_data = bc_local_data.drop(columns=['iso_3166_2_code', 'census_fips_code', 'metro_area'], axis=1)
    bc_local_data.to_csv('bc_local_data.csv')


    print('Finished')

if __name__ == '__main__':
    main()