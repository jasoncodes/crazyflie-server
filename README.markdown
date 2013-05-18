# Installation (Mac OS X)

Make sure you have Homebrew installed then run the following commands:

```
brew install python mercurial libusb pyqt
pip install pyusb
```

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

## Contributors

* Jason Weathered ([jasoncodes])
* Odin Dutton ([twe4ked])

[jasoncodes]: https://github.com/jasoncodes
[twe4ked]: https://github.com/twe4ked
