
## Problem Analytics

To analyze which zip codes are the best to invest in, I need to break down both the profit and cost. Usually, profits come from the value increasing of the property itself and the rental revenue by leasing it out. Cost is more complex, including the original buying price, the tax, the maintenance fee and so on, not to mention the interest and time value of money have been ignored. But the main part is still the property market price. 

Considering the client wants to understand which zip codes would generate the most profit on short term rentals within New York City at this time, I will only consider the rental profit as profit and property market price as cost. The rental profit comes from the property’s rental price and occupancy rate. If Airbnb’s data with one zip code is sufficient enough, we could estimate rental price from it. At the same time, I will build my own model for occupancy rate. 

## Data Shaping and Cleaning

Firstly, in real world, the first data quality issue is, how to tell which information might be useful in the next steps and how to take advantage of those info. In this project, I selected the specific id to track listings. I also extracted scrap/update date info to know the time of listing price, just in case there are price changes for one listing during our observing window. I was not sure whether there will be missing or incorrect values for location and number of bedroom, so I chose space and description as well as all the location information and bedrooms. At last, I am concerned about occupation rate, I thought availability info and reviews might be helpful. Of course, if I have other ideas in the following process, I still could extract the deleted columns from original data frame because I always keep them.

Secondly, I need to subset the listing records for 2 bedrooms within New York city. I used two indicators to filter location: neighbourhood_group_cleansed and City, State, so that I could be more confident that all the records are within NYC. The result is weird: neighbourhood_group_cleansed indicates that all records are within NYC while State tells us that there are three outliers in MP, NJ and VT. If we look at the latitude, longitude and is_location_exact, we would know it could be within NYC. It is so confusing that I doubt whether the host recorded correct information. Since there are only three listings, I chose to delete them. 

Thirdly, since we are going to analyze two bedroom properties, I need to subset the “bedrooms == 2” records. However, does a private room within a two-bedroom count? If so, could I multiply the price of a single room as the rental price of a whole suite? If I did this, could I count a two-bedroom record if a host rent half of his/her 4-bedroom suite? I doubt it. Besides, the good thing is, there are 146 zip codes in total and 296 records for “room type == Private room” and “bedrooms==2”, if I remove all the private room room_type for two-bedrooms, there will be only 2 less data points for each zip code. As a result, I chose to remove those records with “room type == Private room” and “bedrooms==2”.

Fourthly, I also found that there are 62 missing values for zip code, almost 1.3% of the valid data set. Although the rest information, such as street, description, etc., might be sufficient enough to find some zip code back, I deleted them for the time being. Except that, I also need to deal with all the formatting issue with zip code and price. When I aggregate the prices within a zip code, there are some ones with too less data points. I had to drop them to avoid biased result. 

Lastly but most importantly, if I remove those zip codes with too less Airbnb data points, there are 105 zip codes in Airbnb data set while there are far more less zip codes in Zillow’s. If I merge them together according to zip codes, I could only get data for 18 zip codes. Let’s assume that we could estimate the property price of a zip code according to the average price of the zip codes around it. So I found which zip codes are around which zip code first, query their latest price (considering the client wants to buy properties recently) and then calculate the average value, saved it as the median 2-bed home value of the zip code which I could not obtain from Zillow data set directly. With this method, I got 76 (72%) zip codes with a certain value for property price. I think this is good enough for analytics.

## Data Analytics

As I mentioned before, I will calculate how many years it will take to get money back for each zip code. Specifically speaking, if the client buys one 2-bedroom at this time with the median market price within the zip code where it belongs to, and then rent it to short term leasing market to make profit, when we do not consider any other revenue and cost, how long will it take to get all money back?

Let’s look at this equation:
Years to get money back = 
(Current cost to buy a 2-bedroom)

(Occupation rate each year*average price each year*365)

This means I need to estimate the median market price for each zip code, as what I did in the last part of data cleaning. 

To make sure the listings’ prices could represent the price of the whole zip code, I recorded how many listings within one zip code. If the number of hosts within one zip code is sufficient enough, the average price could be estimated by the median/mean price of all the listing price of that zip code. So I removed those zip code with too less listing records and aggregated the price for the left zip codes in my python script.

Apparently, the occupation rate could never be same for all the zip codes. The occupation rate for a hotel near central park could be much higher than a hotel located at somewhere in Staten Island. However, occupation rate could make a great difference for the rental business. So I decided to model it. 

Fortunately for us, our client only wants to compare those zip codes. They care about which ones are better than the rest. Not the exact years to get money back. This means I only need to know the relative occupation rate compared with other zip codes. 

Firstly, I have to assume that the avaibility_30 is updated automatically according to orders in Airbnb’s system. I could not image the host has to update all the availabilities manually. Maybe calendar_update information is used when the host wants to give a time range that the property is used for rent. If he/she wants to hold the listing and occupy the room for his/her own use for a while, he could go to the website and update this info. In this situation, we could trust avaibility_30 is exactly the number of days the property is available for rent within 30 days from the day Airbnb scraped its data.

Secondly, let's assume that customers reserve and cancel all rooms at the same rate for all properties in all the zip codes. In this way, (30 - the availability_30)*“some number” could be the occupation days for past 30 days if we look back at some point 30 days later. 

At this time, 
Years to get money back = 
(Current cost to buy a 2-bedroom)

((30 - the availability_30)*“some number”*average price each year*365)

If we want to compare “years to get money back” among different zip codes, we could just remove “some number”. 

When it comes to the price, I noticed that there is only one price for one listing. This means no price change during our observing window. The issue is, we all know that price could change a lot during different seasons. If we could obtain a whole year’s data from Airbnb, we could aggregate the prices along the year for each listing according to the update date and each price. But we do not have that available. 

Fortunately for us, we only need to conduct analytics for New York City. The climate and the tourist peak should be very similar for all the zip codes. We could assume that the rental price change in a same trend for all the 2-bedrooms within our zip codes. In that way, average price each year for a listing could also be “price on a same day”*“another some number”. Considering all our listing prices have not changed during the observing window, we could think they are the “price on a same day”. 

At this time, 
Years to get money back = 
(Current cost to buy a 2-bedroom)

((30 - the availability_30)*“some number”*observing price*“another some number”*365)

Since I could get rid of those coefficient numbers when comparing them for different zip codes, I could simplify my equation as:
Years to get money back = 
(Current cost to buy a 2-bedroom)

((30 - the availability_30)*observing price*365)

As I mentioned before, I kept zip codes with enough number of listings so that the average rental revenue of the listings from our Airbnb data set could represent that of the corresponding zip code. At this time, all the variables on the right of equation are available and I could move on to calculate my indicator.

## Model Scalability 

The datasets do have different units of time, the price is monthly for Zillow while daily for Airbnb. However, they are separate actions, one for revenue and another for cost, if we do not consider the value increase of the property itself. I do not think they are related with each other, and I do not need to worry about it. When it comes to the different times in Airbnb, we have last_scraped_date, host_since, calendar_updated, calendar_last_scraped, last_review and first_review. Calendar_updated, calendar_last_scraped could be used for availability information, last_scraped_date is more about price duration information. If needed, I could turn all calendar_updated into exact days with regular expression. And then according to calendar last scraped date, give an exact calendar update date. It has been completed in my python script.

If we have more data come in, firstly, it means updated price for Zillow, mighty new zip codes from Zillow. When I extract info from Zillow, I have already taken care of it. I used the whole list of zip codes of Zillow to conduct left merge, extracted the latest price with column number instead of name “2017-06”, in this way, the Zillow part should not be worried about.

Secondly, it means possible new listings and new prices for old listings. Since we have conducted data preprocessing according to its own information, the script should work well to read new data set in similar format. 

Lastly, I left merged two data frames by zip code, this should not be affected by new data set from same data source. Except that zip code is not called “RegionName” in a new data source. Although I could write a function to iterate the column names of a data frame and find one containing “zip”, or iterate the first row of data frame, find the location of a five-digit number/string, and then extract its column name at that location, it still could make mistake, I think it would be better to find that column name according to metadata field description.

## Conclusion Visualization

It is very convenient to conduct visualization in R, especially when it comes to map. I chose ggmap to visualize conclusion. 

After dropping the zip codes with too less data points, throwing away zip codes without an accurate property price after simple imputation, I have 76 zip codes (almost half) with their estimated years to get investment back. By the way, there is a trade-off between data quality and quantity, I assumed client would prefer robust investigation rather than aggressive assumption, otherwise, I could adjust some parameters to improve the available zip codes with a conclusion. 

I put the results in NYC’s google map, if the point is bluer, that zip code is more profitable. If the point is redder, that zip code would take longer to get investment back. 

![](https://raw.github.com/wingsway/BestZipcodesNYC/blob/master/filename.png)

Except the traditional Manhattan central areas (financial district, time square), it seems that Brooklyn is a very promising investment area.

## Further Exploration

For further exploration, firstly, the rental price change could also be taken into account if we could get more data from Airbnb. We could accumulate the price until the date the host changes it. In this way, we could get a more robust price for listings.

Secondly, the property prices could be better estimated if we take other factors into consideration. For instance, instead of taking all the zip codes 1 mile away, if we consider the area of the being estimated zip code, the result might be better. And the income level, education level, community, population could also be both useful and available for zip codes. We could use them to build logistic regression model, train and test the zip codes with known property prices, and then predict the zip codes with unknown property prices

Lastly and most importantly, if our client agrees, I will also take the value increase of the property itself into consideration for profit calculation. Build a regression model for the property price and predict its future changes, this could make our purchase decision much more reliable. 















