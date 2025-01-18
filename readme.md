# setup

## install libraries

apt-get install gcc i2c-tools libgpiod-dev python3-libgpiod python3-sysv-ipc libc6-dev python3-dev

## setup lookback device

### Enable ALSA Loopback Module on Boot
`The ALSA loopback device (snd-aloop) is a kernel module that needs to be loaded on boot.`

Edit the /etc/modules file:

```
sudo nano /etc/modules
```

Add the following line at the end of the file to ensure the snd-aloop module is loaded at boot:

```
snd-aloop
```

Save and exit (Ctrl + O, then Ctrl + X).

### Create a Modprobe Configuration File
We can configure the loopback device using a modprobe configuration.

Create a configuration file for snd-aloop:

```
sudo nano /etc/modprobe.d/aloop.conf
```

Add the following lines to configure the number of loopback devices and subdevices:

```
options snd-aloop enable=1 index=0
options snd-aloop pcm_substreams=2
```

Save and exit (Ctrl + O, then Ctrl + X).

### Update ALSA Configuration
Ensure that the ALSA system recognizes the loopback device.

Create or edit the ALSA configuration file:

```
sudo nano /etc/asound.conf
```

Add the following content to define the loopback device:

```
pcm.!default {
    type plug
    slave.pcm "hw:Loopback,0,0"
}

ctl.!default {
    type hw
    card Loopback
}
```

Save and exit (Ctrl + O, then Ctrl + X).

### Reboot the Raspberry Pi
After making these changes, reboot your Raspberry Pi to apply the settings:

```
sudo reboot
```

### Verify the Loopback Device
After the Pi reboots, check if the loopback device is loaded:

Run the following command to list audio devices:

```
aplay -l
```

You should see an entry like this:

```
card 0: Loopback [Loopback], device 0: Loopback PCM [Loopback PCM]
```
