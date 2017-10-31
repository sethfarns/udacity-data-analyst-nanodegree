
* [Initial Tableau workbook draft](https://public.tableau.com/profile/seth.farnsworth#!/vizhome/MeasuringShanahanEffect-Draft/Story1?publish=yes)
* [Final Tableau workbook draft](https://public.tableau.com/profile/seth.farnsworth#!/vizhome/MeasuringShanahanEffectStory1?publish=yes)

## Summary
In February of 2017, the San Francisco 49ers of the National Football League named Kyle Shanahan as their 19th head coach. Shanahan previously served as offensive coordinator for four separate teams, including with the NFC Champion Atlanta Falcons last year, where his offense boasted the highest scoring total for the season as well as the [eighth-highest scoring offense of all time](https://www.sportingcharts.com/stats/nfl/all-time/most-points-scored-by-an-nfl-team-in-a-season.aspx). Since his hiring by the 49ers, much has been said about [Shanahan's offensive genius](https://www.theringer.com/2017/1/30/16037286/kyle-shanahan-atlanta-falcons-super-bowl-nfl-playoffs-4a40f26c05e2), as well as the [Shanahan effect](http://www.49ers.com/news/ninerfeed/article-2/The-Kyle-Shanahan-Effect-7-Players-Who-Thrived-under-the-49ers-Head-Coach/79b8246c-982c-49be-b385-0efa0c9a928d) on offenses and offensive skill position players, particularly quarterbacks. This project uses advanced offensive performance metrics from [Football Outsiders](http://www.footballoutsiders.com) to attempt to quantify and visualize the effect that Kyle Shanahan has had on offenses and quarterbacks, and how that compares to the performance of other NFL offensive coordinators.

## Design
I used mostly bar charts to visualize the comparison between Kyle Shanahan's offenses and quarterbacks and those of other coaches/coordinators. As each visualization is comparing Kyle Shanahan to other coaches/coordinators, I created a set of "IN/OUT Kyle Shanahan", and used color to distinguish this, with Kyle Shanahan's offenses and quarterbacks highlighted red and everything else gray.

For the chart showing his performance with each team compared to his immediate predecessors and successors, I used bubbles, with the size indicating how long that coach had been with that particular team. I initially tried a bar chart with this one, but I thought it looked too busy. Plus, I wanted to measure the coaches' overall performance with that team rather than just show each individual season.

I tried to keep the designs simple and readable, without too much information to clutter up the view. After receiving some feedback and looking at other students' visualizations, I realized I needed to update my filter and axis titles from their default values to something that would be more descriptive for the viewer. I also added a information box on DVOA (Defense-adjusted Value Over Average), the primary statistic used throughout my Tableau story to compare offensive performance across teams and quarterbacks.

I additionally cleaned up the two charts that dealt with each offensive coordinator's average DVOA performance as well as his differential from the previous coach on that team. I removed all names except for Kyle Shanahan's, and made the bars vertical, to make it easier to see what was going on. I also cleaned up the tool tips, so only pertinent information was displayed and it was more descriptive.

## Feedback
From anamika12545, Udacity student, in Udacity "DAND: Data Visualization with Tableau" Sharing & Feedback section (26 Oct 2017):

> I think this is beautifully done and the visualization paints a very clear picture. The use of color to make the Kyle Shanahan statistics stand out is impressive.

From my father, Don Farnsworth, sent to me personally (28 Oct 2017):

> I really liked the chart on Kyle [Shanahan]'s effect on teams with the red and gray dots, easy to understand and very impressive. My next favorite was [the one] about the [quarterbacks]. My least favorite [was] the comparison of Offensive Coordinators. Busy, needed to be turned 90 degrees. Too many names, differences so slight. Perhaps just use the last 10 years. Now the predictive chart, same criteria for the model as for Kyle [Shanahan]? Was the model for all of the NFL, for how far back?

## Files

* Wrangle DVOA Data.ipynb (code for extracting DVOA and NFL team statistics from Football Outsiders and Pro Football Reference, and cleaning/preparing it for inclusion in Tableau)
* Prep DVOA Data for Machine Learning Model.ipynb (take data prepared in the other notebook and use it to build a machine learning model to predict NFL teams' DVOA)
* dvoa_stats.xlsx (NFL team, quarterback DVOA data for 1986-2017, enriches with coaching data)
* predicted_dvoa.xlsx (model predictions for SF 49ers for 2017 and 2018)

## Resources
* [Football Outsiders](http://www.footballoutsiders.com) (Contained the data for team and quarterback DVOA performance, dating back to 1986)
* [Pro Football Reference](https://www.pro-football-reference.com/) (Information on the coaches for each team)


```python

```
