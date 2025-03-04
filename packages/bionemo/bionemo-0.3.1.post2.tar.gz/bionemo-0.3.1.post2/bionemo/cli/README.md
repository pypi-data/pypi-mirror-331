# Bionemo Command-line Interface

Welcome to the BioNemo commandline-interface (CLI).

## Logging in

To setup your bionemo commandline-interface. Please run `bionemo config set` and enter your API_KEY
and host address credentials. By default your host address should be `https://api.bionemo.ngc.nvidia.com/v1`.

After your credentials have been set, you can view them using `bionemo config show`. If you would like
to see a specific entry of your credentials you can do this by running the command `bionemo config get api_key`
or `bionemo config get host_address`.


## Running tasks

The CLI provides full access to the [BionemoClient's](../api/api.py) public API interface. To see
available CLI options please run
`bionemo --help`
