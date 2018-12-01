![Logo of the project](docs/images/Customer_logo.png)

# Customer &middot; Group 5 &middot; [![Build Status](https://img.shields.io/travis/npm/npm/latest.svg?style=flat-square)](https://travis-ci.org/npm/npm) [![npm](https://img.shields.io/npm/v/npm.svg?style=flat-square)](https://www.npmjs.com/package/npm) [![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com) [![GitHub license](https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square)](https://github.com/your/your-project/blob/master/LICENSE)

Welcome to the Customer Database team. We taking care of registering new customers and logging them in, as well as giving other teams information about the Customer.

## Developing
### Built with
* __Python 3.6__
* __MySQL 8.0__
* Flask 1.0.2
* Flask-SQLAlchemy 2.3.2
    * PyMySQL 0.9.2
* Flask-RESTful 0.3.6
* Flask-JWT-Extended 3.13.1
* passlib 1.7.1
    * argon2-cffi 18.3.0

## Prerequisites
* __[Git](https://git-scm.com/downloads)__
* __[Docker](https://www.docker.com/get-started)__

## Setting up Dev
__Make sure you have installed Git and Docker before doing the commands below.__

1. Set Environment variables
    You need to set the following Environment variables. The keys needs to be _exactly_ as written here, but you choose the values to your liking.
    How to set Environment variables is described here: https://www.twilio.com/blog/2017/01/how-to-set-environment-variables.html

    * MySQLPassword
    * CustomerSecret

1. Clone the repository from github so you get all the necessary files

    ```shell
    git clone https://github.com/DAT210/Customer.git
    cd Customer/
    docker-compose up --build
    ```

    * The following happens when you executes those commands:

        1. Clones the project to your computer

        1. Change directory into the project you just cloned

        1. Docker does a lot of stuff.

        1. Docker installs everything under [_built with_](#built-with)

        1. Docker sets up the database

        1. Docker runs the flask app

1. Ready to receive requests

&nbsp;

### IP address to send requsts to:

* If you are using docker toolbox, the address is  http://192.168.99.100:25201/
* If you are using the new docker, the address is  http://127.0.0.1:25201/

> Note: If you change anything in the files of the composer, you need to stop the container and run it again for the changes to take effect. How to do that in _Useful for testing_ below.

&nbsp;

### Useful for testing

* If you want to reset the database, stop container if running and use these commands:
    ```shell
    docker-compose down -v
    docker-compose up --build
    ```
* If you want to query directly into the database use this command, then treat it like you are using SQL statements.
    > Note: The container you started in step 2 must be running before executing this command.
    
    > __Use caution while using this. If you mess up, reset the database as described above.__
    
    ```shell
    docker exec -it customer_db_1 mysql -uroot -p
    ```

## API Reference

__Important:__ Keep in mind that how you send the requests to us may change in the future.

With our Api you can get the name, email and Customer Identification Number(cid) of the customer, more will come in the future.

_If you are new to our API, please read the full documentation: [Docs](/docs)_

> If you really want to get quickly started see our [_Full example_](docs/usage.md#full-example), but its recommended to read through _How to use the API_ in [_Usage_](docs/usage.md).

If you want to go straight to how to use the API, go to [_Usage_](docs/usage.md).

### Very brief about how to use the API

In order to obtain information about the Customer, send a get-request with the authorization header you got from the client as an authorization header(how to do that is in Usage docs linked above). Use the base address in the "setting up dev" section with one of the following URIs attached:

* /v1/customer/cid
* /v1/customer/email
* /v1/customer/name

> For example, if you are using the new docker, send a get request to 127.0.0.1:25201/v1/customer/cid to get the cid of the currently logged in customer.