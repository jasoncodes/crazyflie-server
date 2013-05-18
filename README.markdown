# Installation (Mac OS X)

Follow the [installation instructions](http://wiki.bitcraze.se/projects:crazyflie:pc_utils:install#installing_on_mac_osx) on the Crazyflie wiki. You’ll also need to also install `libusb` with `brew install libusb`.

Clone this project:

``` sh
mkdir -p ~/projects
cd ~/projects
git clone https://github.com/jasoncodes/crazyflie-server
```

Clone the [Crazyflie PC client](https://bitbucket.org/bitcraze/crazyflie-pc-client):

``` sh
cd ~/projects
hg clone https://bitbucket.org/bitcraze/crazyflie-pc-client
```

Link the Crazyflie PC client library into the server project:

```
cd ~/projects/crazyflie-server
ln -s ../crazyflie-pc-client/lib
```
