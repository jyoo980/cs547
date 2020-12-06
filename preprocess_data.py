import pandas as pd
import numpy as np
import scipy.stats
import datetime as dt
import math

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

def calculate_bayesian_surprise():
    df = pd.read_csv('new_data/provincial_data.csv')
    surprise_df = df.copy()
    equality_mean = 0
    equality_std = 2

    canada_population = 38005238
    province_population = {
        'CA-ON': 14734014,
        'CA-QC': 8574571,
        'CA-BC': 514712,
        'CA-AB': 4421876,
        'CA-MB': 1379263,
        'CA-SK': 1178681,
        'CA-NS': 979351,
        'CA-NB': 781476,
        'CA-NL': 522103,
        'CA-PE': 159625,
        'CA-NT': 45161,
        'CA-NU': 39353,
        'CA-YT': 42052 
    }
    province_mean = {
        'CA-ON': 0,
        'CA-QC': 0,
        'CA-BC': 0,
        'CA-AB': 0,
        'CA-MB': 0,
        'CA-SK': 0,
        'CA-NS': 0,
        'CA-NB': 0,
        'CA-NL': 0,
        'CA-PE': 0,
        'CA-NT': 0,
        'CA-NU': 0,
        'CA-YT': 0 
    }
    province_std = {
        'CA-ON': province_population['CA-ON']/canada_population,
        'CA-QC': province_population['CA-QC']/canada_population,
        'CA-BC': province_population['CA-BC']/canada_population,
        'CA-AB': province_population['CA-AB']/canada_population,
        'CA-MB': province_population['CA-MB']/canada_population,
        'CA-SK': province_population['CA-SK']/canada_population,
        'CA-NS': province_population['CA-NS']/canada_population,
        'CA-NB': province_population['CA-NB']/canada_population,
        'CA-NL': province_population['CA-NL']/canada_population,
        'CA-PE': province_population['CA-PE']/canada_population,
        'CA-NT': province_population['CA-NT']/canada_population,
        'CA-NU': province_population['CA-NU']/canada_population,
        'CA-YT': province_population['CA-YT']/canada_population 
    }

    equality_prob = 0.5
    population_prob = 0.5

    categories = ['retail_and_recreation_percent_change_from_baseline', 
    'grocery_and_pharmacy_percent_change_from_baseline',
    'parks_percent_change_from_baseline',
    'transit_stations_percent_change_from_baseline',
    'workplaces_percent_change_from_baseline',
    'residential_percent_change_from_baseline']


    category_std_multiplier = {
        'retail_and_recreation_percent_change_from_baseline': 1, 
        'grocery_and_pharmacy_percent_change_from_baseline': 1,
        'parks_percent_change_from_baseline': 5,
        'transit_stations_percent_change_from_baseline': 1,
        'workplaces_percent_change_from_baseline': 1,
        'residential_percent_change_from_baseline': 3
    }

    category_mean = {
        'retail_and_recreation_percent_change_from_baseline': 1, 
        'grocery_and_pharmacy_percent_change_from_baseline': 1,
        'parks_percent_change_from_baseline': 1,
        'transit_stations_percent_change_from_baseline': 1,
        'workplaces_percent_change_from_baseline': 1,
        'residential_percent_change_from_baseline': 1
    }

    category_std = {
        'retail_and_recreation_percent_change_from_baseline': 1, 
        'grocery_and_pharmacy_percent_change_from_baseline': 1,
        'parks_percent_change_from_baseline': 1,
        'transit_stations_percent_change_from_baseline': 1,
        'workplaces_percent_change_from_baseline': 1,
        'residential_percent_change_from_baseline': 1
    }

    for category in categories:
        category_values = df[category].values
        category_values = category_values[np.logical_not(np.isnan(category_values))]
        category_min = np.min(category_values)
        category_max = np.max(category_values)
        modifier = (np.abs(category_max) + np.abs(category_min))
        category_std_multiplier[category] = category_std_multiplier[category] * modifier

    for category in categories:
        category_values = df[category].values
        category_values = category_values[np.logical_not(np.isnan(category_values))]
        m = np.mean(category_values)
        s = np.std(category_values)
        category_std[category] = s
        category_mean[category] = m


    start_date = pd.to_datetime('2020-02-15')
    end_date = pd.to_datetime('2020-10-18')
    for index, row in df.iterrows():
        prov = row['iso_3166_2_code']
        date = row['date']
        row_id = row[0]
        mask = df['date'] == date
        current_date_values = df.loc[mask]
        for category in categories:
            temp1 = row[category]
            if not np.isnan(row[category]):
                category_values_on_date = current_date_values[category].values
                category_values_on_date = category_values_on_date[np.logical_not(np.isnan(category_values_on_date))]
                category_mean_on_date = np.mean(category_values_on_date / 100)
                category_std_on_date = np.std(category_values_on_date / 100)
                category_value = row[category] / 100

                equality_likelihood = scipy.stats.norm(category_mean_on_date, equality_std).cdf(category_value)
                # population_likelihood = scipy.stats.norm(province_mean[prov], province_std[prov]*5).cdf(category_value)
                population_likelihood = scipy.stats.norm(province_mean[prov], province_std[prov] * category_std_multiplier[category] * 10).cdf(category_value)

                equality_prob = equality_prob
                population_prob = population_prob

                data_prob = scipy.stats.norm(category_mean_on_date, category_std[category]).cdf(category_value)

                equality_posterior = equality_likelihood * equality_prob / data_prob
                population_posterior = population_likelihood * population_prob / data_prob

                kl_divergence = equality_posterior * np.log(equality_posterior / equality_prob) + \
                                population_posterior * np.log(population_posterior / population_prob)

                if math.isnan(kl_divergence):
                    print('here')
                # print(kl_divergence)
                # print(surprise_df.iloc[index][category])

                surprise_df.loc[index, category] = kl_divergence
                # print(surprise_df.iloc[index][category])
            else:
                # print("i'm here")
                hi = 'hi'

    surprise_df.to_csv('new_data/province_surprise_data.csv')
    print('done')

    for category in categories:
        category_values = surprise_df[category].values
        category_values = category_values[np.logical_not(np.isnan(category_values))]
        category_min = np.min(category_values)
        category_max = np.max(category_values)
        print(category)
        print('max', category_max)
        print('min', category_min)

    return  

if __name__ == '__main__':
    # main()
    calculate_bayesian_surprise()