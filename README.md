# BirthChart Web Application

BirthChart is a web-application that calculates user's birth chart shows their daily horoscope.

## Libaries Used

[kerykeion](https://github.com/g-battaglia/kerykeion)
[aztro](https://github.com/sameerkumar18/aztro)

## Description

BirthChart calculates and displays the birth chart of the user in accordance with the information provided by the user and the chart selected. In addition, it also shows the user daily horoscope. Furthermore, with the information on the Homepage and About Astrology page, it is aimed for the user to have more information about Astrology and charts.

My initial goal was for charts to be selected when filling out the form, but considering that different charts have different requirements and results, I moved the chart selection to a different HTML file. I also built the pages showing each chart in different HTML files because the result I wanted was different for each chart and I thought it would be easier.

As for the Stored Data part, my initial aim was to save the birth information of the users and enable them to access their charts with the click of a button. However, since I could not generate a unique ID for each button, I gave up on this idea and decided to show only the recorded birth information in tabular form. If you would like to contribute to this issue, pull requests are welcome.

![Stored Data](https://github.com/karakuscem/Birth-Chart/blob/master/images/Stored%20Data.png)

I used kerkeion library for charts. This library calculates the natal chart and outputs it as an SVG file if you wish. There is also a relationship score calculation feature for the Synastry map. For the daily horoscope, I used the library called aztro. This library is for pulling daily horoscope comments from a particular site. Aztro takes the abbreviated names of the constellations as input, but kerykeion gives the full names of the constellations as output. So I created a dictionary in ***helpers.py*** and changed the value sent by kerykeion to a value that aztro would accept. Thus, a daily horoscope is obtained according to the user's Sun sign in line with the information entered by the user.

![Birth Chart and Daily Horoscope](https://github.com/karakuscem/Birth-Chart/blob/master/images/Natal%20Chart%20and%20Daily%20Horoscopes.png)
![Synastry Chart and Daily Horoscope](https://github.com/karakuscem/Birth-Chart/blob/master/images/Synastry%20chart.png)

## Usage

The application uses the 24-hour time format. To use the application, you must enter your full birth information. If you do not know the hour and minute of your birth, you can enter the hour and minute as ***"00"(12 a.m)***. Although your time of birth is important, a birth chart can provide you with important information even if you don't know it.

## Contributing

Pull requests are welcome.
