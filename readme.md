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

Example compiled command on windows

```shell
dist/MusicLEDStreamer.exe run stars 1 directx 1080 1920 44100 2 39
```

- command: run
- show: stars
- display: 1
- video_driver: directx
- screen_width: 1080
- screen_height: 1920
- samplerate: 44100
- channels: 2
- device_index: 39
- blocksize: default of 1024
- latency: default of 0.1

Example compiled command on linux

```shell
dist/MusicLEDStreamer.exe run stars 1 directx 1080 1920 44100 2 39
```

- command: run
- show: stars
- display: :0 (default displayh)
- video_driver: x11
- screen_width: 800
- screen_height: 600
- samplerate: 44100
- channels: 2
- device_index: 1
- blocksize: default of 1024
- latency: default of 0.1
