

# Toychest
This is made to automate my silly gimmicks which I have nowhere to host.

# Structure
* `toycommons`: To-be subrepo of common functionality. Config, database access, logging.
Should be initialized with just database credentials and expects to be hosted on the `toynet`/`toysupport`
* `toychest`: Static front-page serve. Uses `toycommons`
* `toydiscover`: Private reporter of connected services. Uses `toycommons`
* `nginx`: Main router configuration

## Docker
* Networks: Via the script everything should be at two main networks, outer and inner.
* Volumes: Via the script everything should be at logging volume
* 

# Functionality
* Static page as a root route for the host
* Scripts and help guides to deploy/backup/destroy anything as a container

## Submodule
* Common initializing interface for accessing configuration
* Common logging setup to unify structure
* Automatic reporting of a tool for discovery purposes