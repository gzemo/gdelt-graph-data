# GDELT Graph Data

The current repository provides a simple data processing pipeline that gathers event information from the *GDELT* project (v.2.0 Event data) in order to provide a daily adjacency matrix that models the worldwide countries relationships through time.

This project is a spin-off from an analysis that addressed the mutual influence of countries foreing affairs (*see:* https://github.com/gzemo/relations-of-power-between-countries).

---

## Time interval

From 1 January 2018 - ongoing


## Data
Adjacency matrices are already downloaded and converted and can be found in `./networks` in the following format `./networks/YYYYMMDD_networks.zip`. <br/>
Each compressed file containts the `npy` Python numpy file that can be loaded by:

```python
year, month, day = "2024", "04", "16" 
day_matrix = np.load(f"{year}{month}{day}_network.npy")
```

## Unzip and read

```python
import zipfile

def read(filepath, outdir):
	with zipfile.ZipFile(filepath, "r") as zf:
		zf.extractall(outdir)
```


## Daily graph estimation

1. **Single-update graph estimation:** the single 15 minute interval update graph is estimated by assigning to each pair of countries involved in each entry the corresponding weight (*see below*) generating the $G_k^{[update]}$ graph with $k=1, .., N_{updates}$.

2. **Daily-updates graph estimation:** the complete set of 15 minutes time interval updates of a given day (as in Point *#1*) is processed and the edgewise values are summed, yielding the $G_d^{[day]}$ graph with $d=1, .., N_{days}$.


## Edge connectivity estimation

The way in which the countries’ relationships had been formalized relies on a composite score which takes into account the information available from the list of filtered event features. The resulting edge value between nodes $(i,j)$ that defines the degree to which an alliance is occurring between that pair of countries mostly depends on the Goldstein Score ($GS$). Minor relevance is given by the news coverage information such as the *a)* number of sources, *b)* number of articles and *c)* the average tone (formalised respectively by $(s, a, T)$ in the equation below) by tuning their weighting factors $\theta_1, \theta_2, \theta_3$ in a $[0,1]$ range:

![alt text](./pics/edge_estimation.png?raw=true)


## Credits

- *The GDELT project*: https://www.gdeltproject.org/
- Countries ISO code: *Wikipedia®* https://en.wikipedia.org/wiki/List_of_ISO_3166_country_code