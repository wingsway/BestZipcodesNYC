library(zipcode)
library(ggmap)
setwd("/Users/wenying/Downloads")
nycZipValue = read.csv("output.csv",na.strings=c(""," ","NA"))
data(zipcode)
# it seems like 10004 goes to NJ. But that is because 10004 also includes governors island, 
# part of Ellis Island and Statue of Liberty National Monument
nycZipValue = merge(nycZipValue,zipcode,by.x='zipcode',by.y='zip',all.x=TRUE)
###g = ggplot(data=zipcode) + geom_point(aes(x=longitude, y=latitude, colour=region))
myMap = get_map(location=c(lon=-73.99019,lat=40.75951),zoom=12)
ggmap(myMap)
ggmap(myMap)+
  geom_point(aes(x = nycZipValue$longitude, y = nycZipValue$latitude, colour = nycZipValue$break_even_years), data = nycZipValue,
             size = 3) + scale_colour_gradient(low = 'blue',high = 'red') +
  geom_text(aes(x = nycZipValue$longitude, y = nycZipValue$latitude, label = nycZipValue$zipcode), data = nycZipValue,
             size = 1, colour = "white") +
  ggtitle("How many years it take to get investment back in each zip code")