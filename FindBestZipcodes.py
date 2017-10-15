import pandas as pd
import numpy as np
# get the width of the terminal window, so that I could divide the screen for better readability
terminal_width = pd.util.terminal.get_terminal_size()[0]
# read in the 2 csv files
airbnb_df = pd.read_csv('~/Downloads/airbnb-zillow-data-challenge-master/listings.csv', dtype={'id':object, 'scrape_id':object, 'zipcode':object})
zillow_df = pd.read_csv('~/Downloads/airbnb-zillow-data-challenge-master/Zip_Zhvi_2bedroom.csv', dtype={'RegionID':object, 'RegionName':object})
# all the ids should be read as object
print "get the info of airbnb_df:"
print(airbnb_df.columns.values)
print(airbnb_df.head())
print airbnb_df.info()
print("#"*terminal_width)
#remove the unnecessary info
airbnb_nyc = airbnb_df[['id','scrape_id','last_scraped','space','description','street','neighbourhood',
'neighbourhood_cleansed','neighbourhood_group_cleansed','city','state','zipcode',
'market','smart_location','country_code','country','latitude','longitude','is_location_exact',
'availability_30','availability_60','availability_90','availability_365','number_of_reviews','host_since',
'first_review','last_review','room_type','bedrooms','price','calendar_updated','calendar_last_scraped']]
print "get the info of zillow_df"
print(zillow_df.columns.values)
print(zillow_df.head())
print zillow_df.info()
print("#"*terminal_width)
# Find the records within NYC
print "Find whether there are records outside NYC"
print airbnb_nyc.neighbourhood_group_cleansed.unique()
print airbnb_nyc.state.unique()
# this is weird, let's look at these records
print airbnb_nyc[(airbnb_nyc['state'] == 'MP')|(airbnb_nyc['state'] == 'NJ')|(airbnb_nyc['state'] == 'VT')]
print("#"*terminal_width)
# if we look at the latitude and longitude, we would know it is within NYC, but the rest location info is conflicting
# since there are only 3 records here, I will delete these three
airbnb_nyc = airbnb_nyc[(airbnb_nyc['state'] == 'ny')|(airbnb_nyc['state'] == 'NY')|(airbnb_nyc['state'] == 'New York')]
#print airbnb_nyc.info()
# there are 40681 valid values for bedrooms, which means we have 69 missing values, I might be able to find back them according to space/description,
# but at this time, we could just leave them behind
airbnb_nyc_2b = airbnb_nyc[(airbnb_nyc['bedrooms'] == 2)]
print "get the info of records with 2 bedrooms and located in NYC"
print airbnb_nyc_2b.info()
print airbnb_nyc_2b.describe()
print("#"*terminal_width)
# there are 62 missing values for zipcode, almost 1.3%, although the rest information may be sufficient enough to find some zipcode back,
# I will delete these records at this time
airbnb_nyc_2b = airbnb_nyc_2b[airbnb_nyc_2b['zipcode'].notnull()]
print "conduct data cleaning for zip code and price"
print airbnb_nyc_2b.zipcode.unique()
# data cleaning is needed for zipcode
airbnb_nyc_2b['zipcode'] = airbnb_nyc_2b['zipcode'].map(lambda x: x.split('-')[0])
print airbnb_nyc_2b.zipcode.unique()
# I am not sure whether the hosts have updated the listing price during our observing window, so I need to see whether those listings are unique
print airbnb_nyc_2b['id'].nunique()
# there are 4831 ids here, this means one record for one listing, specifically speaking, this means one price for one listing
# data cleaning for the price
airbnb_nyc_2b['price'] = airbnb_nyc_2b['price'].map(lambda x: float(x[1:].replace(',', '')))
print airbnb_nyc_2b['price'].describe()
print("#"*terminal_width)
# the min price and max price do not make too much sense here, but the good thing is,
# the Quantiles are reasonable, maybe we could remove the outliers in further analytics
print "consider whether to keep private room for 2 bedrooms"
print airbnb_nyc_2b.room_type.unique()
# I am not sure whether all the prices mean the price for the whole 2b property, so I need to look at room_type
# the result is ['Entire home/apt' 'Private room']
# I have to make a decision here, to drop off all the 'Private room'? or multiply their price by 2?
# Another decision is, shall I use mean or median for the average 2b property price within one zipcode?
print airbnb_nyc_2b.groupby('room_type').size()
print("#"*terminal_width)
# There are 146 zipcodes here and 296 records for Private room, if I remove all the private room room_type,
# there will be only 2 less data points for each zipcode
# As a result, for initial analytics, I choose to just keep 'Entire home/apt' records
# Besides, I use median price for consistancy with zillow data
airbnb_nyc_2b = airbnb_nyc_2b[(airbnb_nyc_2b['room_type'] == 'Entire home/apt')]
airbnb_nyc_2b_price = airbnb_nyc_2b[['zipcode','price']]
# data cleaning with the calendar_updated date
def g(x):
    res = 0
    if "today" in x:
        res = 0
    elif "yesterday" in x:
        res = 1
    elif "days" in x:
        res = int(x.split()[0])
    elif "a week" in x:
        res = 7
    elif "weeks" in x:
        res = 7*int(x.split()[0])
    elif "a month" in x:
        res = 30
    elif "months" in x:
        res = 30*int(x.split()[0])
    else:
        res = 3650
    return res

airbnb_nyc_2b['exact_update_days'] = airbnb_nyc_2b['calendar_updated'].map(g)
airbnb_nyc_2b['exact_update_date'] = pd.to_datetime(airbnb_nyc_2b.calendar_last_scraped) - pd.to_timedelta(pd.np.ceil(airbnb_nyc_2b.exact_update_days), unit='D')

# Calculate accumulated price, count, occupationrate for each zipcode
# To estimate occupation rate, let's assume that customers reserve and cancel all rooms at the same rate
# for all properties in all the zipcodes. Which means, (30 - the availability_30)*some number could be
# the occupation days for past 30 days if we look back at some point 30 days later
airbnb_nyc_2b_occupationrate = airbnb_nyc_2b[['zipcode','availability_30']]
airbnb_nyc_2b_occupationrate['occupationrate'] = 1 - airbnb_nyc_2b_occupationrate['availability_30']/30
airbnb_nyc_2b_occupationrate = airbnb_nyc_2b_occupationrate[['zipcode','occupationrate']]
airbnb_nyc_2b_price_by_zipcode = airbnb_nyc_2b_price.groupby('zipcode', as_index=False).median()
airbnb_nyc_2b_occupationrate_by_zipcode = airbnb_nyc_2b_occupationrate.groupby('zipcode', as_index=False).median()
airbnb_nyc_2b_count_by_zipcode = airbnb_nyc_2b_price.groupby('zipcode', as_index=False).count()
airbnb_nyc_2b_count_by_zipcode = airbnb_nyc_2b_count_by_zipcode.rename(columns = {'price':'rental_data_points_count'})

airbnb_nyc_2b_by_zipcode = pd.merge(airbnb_nyc_2b_price_by_zipcode, airbnb_nyc_2b_count_by_zipcode,left_on = 'zipcode', right_on = 'zipcode')
airbnb_nyc_2b_by_zipcode = pd.merge(airbnb_nyc_2b_by_zipcode, airbnb_nyc_2b_occupationrate_by_zipcode, left_on = 'zipcode', right_on = 'zipcode')
print "show the accumulated price, count, occupationrate for each zipcode"
print airbnb_nyc_2b_by_zipcode
# To get robust result, I drop the zipcodes with too less data points
print airbnb_nyc_2b_by_zipcode.describe()
# the median is 9, the 25% is 3
airbnb_nyc_2b_by_zipcode = airbnb_nyc_2b_by_zipcode[(airbnb_nyc_2b_by_zipcode['rental_data_points_count']>3)]
print("#"*terminal_width)
# join data from zillow
lastest = len(zillow_df.columns) - 1
zillow_df = pd.concat([zillow_df.ix[:,1],zillow_df.ix[:,lastest]], axis=1)
zillow_df.columns = ['RegionName','propertyPrice']
main_df = pd.merge(airbnb_nyc_2b_by_zipcode, zillow_df, left_on = 'zipcode', right_on = 'RegionName', how = 'left')
print main_df.info()
# Since we are going to purchase properties recently, I used the latest price, which is the last column
print "only 18 records with a property price"
print("#"*terminal_width)
# In the following, I will try to match the property price according to adjacent zipcodes
import zipcode
import zipcodes
# estimate the missing property prices
main_df['adjacentZipcodes'] = main_df['zipcode'].map(lambda x: zipcode.isinradius((zipcodes.matching(x)[0]['lat'],zipcodes.matching(x)[0]['long']),1))
# save zipcodes with actual property price into a dict
actualPrices = main_df[['RegionName','propertyPrice']].set_index('RegionName')['propertyPrice'].to_dict()
def f(x):
    res = []
    for i in x:
        if i.zip in actualPrices.keys():
            res.append(actualPrices[i.zip])
    return np.mean(res)

main_df['propertyPrice1st'] = main_df['adjacentZipcodes'].map(f)
main_df['estimatePrice'] = main_df['propertyPrice']
main_df.estimatePrice.fillna(main_df.propertyPrice1st, inplace=True)
print "the number of zip codes with a property price:"
print main_df['estimatePrice'].count()
# 76
# Found back 72% of property price, good enough for analytics

# Calculate how many years it takes to get all money back for each zipcode
main_df['break_even_years'] = main_df['estimatePrice']/(main_df['price']*main_df['occupationrate']*365)
main_df = main_df[['zipcode','break_even_years','rental_data_points_count']]
main_df = main_df[(main_df['break_even_years']<100)]
print("#"*terminal_width)
print "show the zip codes and their ability to make profit in Desc order:"
print main_df.sort_values('break_even_years')

# output the result
main_df.to_csv('output.csv', index=False)

# I will switch to R for visualization
