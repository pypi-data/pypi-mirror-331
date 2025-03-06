# Cloudlab Client

This package is a client for the Cloudlab service. Cloudlab is a cloud for
academic institutions. Because I could not (yet) find any working API for
Cloudlab, the current client relies on username / password authentication and
web scraping.


## Usage


```python
# Create new client and login
username = os.environ.get("CLOUDLAB_USERNAME")
password = os.environ.get("CLOUDLAB_PASSWORD")
cloudlab_client = CloudlabClient()
cloudlab_client.login(username, password)

# List experiments
experiments = cloudlab_client.experiment_list()
print(experiments)

# List an experiment's nodes
nodes = cloudlab_client.experiment_list_nodes("my-experiment")
print(nodes)

# Request an extension (e.g., for 6 days). Reason must be at least 120 characters.
reason = ("Important experiment needed for research, conducted under advisor"
          " <fill_your_advisor>. Particular machines are needed because"
          " <fill_your_reasons>.")
cloudlab_client.experiment_extend("my-experiment", reason, hours=6*24)
```
