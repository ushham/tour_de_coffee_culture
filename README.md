# Tour de Coffee Culture
## Description
The Tour de [Coffee Culture](https://coffeeculture.co.nz/tour-de-coffee-culture-2026/canterbury-tour) is a challenge to cycle to all of the Coffee Culture branches in a single day. This repo solves the [travelling salesman problem](https://en.wikipedia.org/wiki/Travelling_salesman_problem) to find the optimal route, for the following variables:
- Shortest Distance
- Least vertical elevation
- Fastest time (given cycling performance and wind)

[GraphHopper](https://www.graphhopper.com/) was used to find the best cycling route between each cafe. The free version was used, so there are some routes (Bridle path out of Lyttelton for example) that may not be suitable for roadbikes.

A model of speed given the riders power was used to calculate the approximate speed for each route. This has limitations as it does not take into account real world conditions like traffic lights, or road surface.

For more details see my post about this: 

## Usage
To find out the shortest path for your set up, power output, and weather conditions, update the notebook `Fastest-time-solution.ipynb`. The cycling model allows for the following user set parameters:
```{python}
cycling_parameters = {
    "power_output": 100,      # average power in watts
    "weight": 65,             # rider weight in kg
    "bike_weight": 12,        # kg
    "drive_train_loss": 0.02, # proportion between 0-1
    "area": 0.509,            # Cross section area of rider m^2
    "air_density": 1.22601,   # kg/m^3
    "cda": 0.4,
    "coef_rolling_resistance": 0.005,
    "max_speed": 45,          # km/h - prevents huge speeds downhill
    "min_speed": 8,           # km/h
    "corner_time_penalty": 5  # Max time penalty for harsh corner
}
```

If you want to use Graphhopper to construct new routes between each cafe, add a `config.yaml` file with the following:

```{yaml}
api: YOUR_KEY
```

## Assumptions
### Cycling model
The model to calculate an average speed given the above parameters was influenced by [Steve Gribble](https://www.gribble.org/cycling/power_v_speed.html). This balences the forces of gravity, wind resistance (including headwinds) and rolling resistance, with the power input by the cyclist to find the resulting speed. 

A very simple penilty has been added to help reflect the reduced speeds in cities. The harsher the corner a cyclist must take, the harsher the time penilty.

Maximum and minimum speed limits have been added to prevent huge downhill speeds, and crawling slower than walking pace uphill. 

### Routes

Road surfaces are assumed to be constant. This is clearly not true for some of the routes that are included in this.

To reduce API calls, the routes between cafes have been assumed to be symmetric. This means the route taken from A -> B is the same as B -> A.

### Weather
When wind is included, it is included at the same rate, from the same direction, across all routes. In other-words, no local variation to wind direction or wind speed is taken into account.

## Results
The shortest possible route is 109.5km, with 870m of vertical elevation. Using a cycling model that is based off of my very average cycling ability, it should take me no less than 4.5 hours.

The fastest way to do the loop is a little longer at 112km, but would take a whole 4minutes less than the shortest route, due to less climbing.

If you want to get the fastest time possible (estimated at 4hr 12 mins for me), do the ride in a strong south-westerly wind (213° to be exact).

Here is a summary table of distances and times for each wind direction:



| Wind	| Time (min) | Distance (km) |	Elevation (m) |
| --- | --- | --- | ---|
| Shortest Distance | 274 |	109.5 |	870 |
| Least Climbing | 295 | 125.8 | 552 |
|No wind |	270 | 111.9 | 857 |
| Northerly	| 258 | 110.5 |	843 |
| Southerly	| 258 |	111.9 |	857 |
| Westerly | 296 | 110.5 | 844 |
| Easterly | 304 | 118.4 |	552 |
| North Westerly | 275 | 110.5 | 844|
| Best wind | 252 |111.9 |	857 |